import logging
import os.path

from storage.interfaces.FileManager import FileManager
from storage.implementations.FtpFileManager import FtpFileManager

SECOND = 2

BEFORE = "before"

ACTUAL = "actual"

FIRST = 1

logger = logging.getLogger('Sync algorithm')


class InitAlgorithm:
    def __init__(self, first_manager: FileManager, second_manager: FileManager):
        self.first_manager, self.second_manager = first_manager, second_manager
        self.tmp_file = 'tmp.file'
        self.is_first_level = True
        self.snapshots = {
            FIRST: {
                ACTUAL: dict(),
                BEFORE: dict()
            },
            SECOND: {
                ACTUAL: dict(),
                BEFORE: dict()
            }
        }

        self.level_snapshots = {
            FIRST: dict(),
            SECOND: dict()
        }
        self.dir_list = list()

    def copy_file(self, file, first_manager, second_manager):
        if isinstance(first_manager, FtpFileManager) \
                and isinstance(second_manager, FtpFileManager):
            with open(self.tmp_file, 'wb') as fd:
                first_manager.retrieve_file(file, fd)
            with open(self.tmp_file, 'rb') as fd:
                second_manager.save_file(file, fd)

        elif isinstance(first_manager, FtpFileManager):
            fd = second_manager.open(filename=file, mode='w')
            first_manager.retrieve_file(filename=file, fd_dest=fd)
            second_manager.close(fd=fd)
        else:
            fd = first_manager.open(filename=file, mode='r')
            second_manager.save_file(filename=file, fd_source=fd)
            first_manager.close(fd=fd)

    def syncronize_locations(self, first_meta, first_manager,
                             second_meta, second_manager):
        for file in first_meta:
            if file in second_meta and first_meta[file] < second_meta[file]:
                continue
            self.copy_file(file=file, first_manager=first_manager, second_manager=second_manager)

    def save_meta_to_current_snapshot(self, meta_dict):
        for man_index in [FIRST, SECOND]:
            self.level_snapshots[man_index] = dict()
            for element in meta_dict[man_index]:
                modified_time = meta_dict[man_index][element]
                full_path = os.path.join(*self.dir_list, element)
                self.snapshots[man_index][ACTUAL][full_path] = modified_time
                self.level_snapshots[man_index][full_path] = modified_time

    def __run__(self):
        if len(self.dir_list) == 0:
            logging_dir = "base dir"
        else:
            logging_dir = os.path.join(*self.dir_list)
        logger.info("Running script on dir: {}".format(logging_dir))

        first_meta = self.first_manager.get_files_metadata()
        second_meta = self.second_manager.get_files_metadata()

        self.save_meta_to_current_snapshot({FIRST: first_meta, SECOND: second_meta})

        self.syncronize_locations(first_meta, self.first_manager,
                                  second_meta, self.second_manager)
        self.syncronize_locations(second_meta, self.second_manager,
                                  first_meta, self.first_manager)

        first_dirs = set(self.first_manager.get_dirs())
        second_dirs = set(self.second_manager.get_dirs())

        all_dirs = set(first_dirs) | set(second_dirs)
        first_to_be_added = all_dirs - first_dirs
        second_to_be_added = all_dirs - second_dirs
        for directory in first_to_be_added:
            self.first_manager.create_dir(directory)
        for directory in second_to_be_added:
            self.second_manager.create_dir(directory)

        for directory in all_dirs:
            self.first_manager.dive_into_dir(directory)
            self.second_manager.dive_into_dir(directory)
            self.dir_list.append(directory)
            print(self.dir_list)
            self.__run__()
            self.dir_list.pop()
            self.first_manager.leave_dir()
            self.second_manager.leave_dir()

    def run(self):
        self.first_manager.setup()
        logger.info("Setup for first manager succeeded")
        self.second_manager.setup()
        logger.info("Setup for second manager succeeded")
        self.__run__()
        for man_index in [FIRST, SECOND]:
            self.snapshots[man_index][BEFORE] = dict(self.snapshots[man_index][ACTUAL])

    def remove_file(self, file: str, manager: FileManager):
        manager.remove_file(filename=file)

    def refresh_location(self, first_manager, second_manager,
                         first_level, second_level,
                         first_before, second_before):

        for element in first_level:
            first_best_date = max(first_level[element], first_before.get(element, 0))
            second_best_date = max(second_level[element], second_before.get(element, 0))
            if first_best_date > second_best_date:
                file = os.path.basename(element)
                self.copy_file(file=file, first_manager=first_manager, second_manager=second_manager)

        for element in first_before:
            if element in first_level:
                continue
            file = os.path.basename(element)
            self.remove_file(file=file, manager=second_manager)

    def __keep_syncronized__(self):
        first_meta = self.first_manager.get_files_metadata()
        second_meta = self.second_manager.get_files_metadata()

        self.save_meta_to_current_snapshot({FIRST: first_meta, SECOND: second_meta})
        self.refresh_location(first_manager=self.first_manager, second_manager=self.second_manager,
                              first_level=self.level_snapshots[FIRST],
                              second_level=self.level_snapshots[SECOND],
                              first_before=self.snapshots[FIRST][BEFORE],
                              second_before=self.snapshots[SECOND][BEFORE])

        self.refresh_location(first_manager=self.second_manager, second_manager=self.first_manager,
                              first_level=self.level_snapshots[SECOND],
                              second_level=self.level_snapshots[FIRST],
                              first_before=self.snapshots[SECOND][BEFORE],
                              second_before=self.snapshots[FIRST][BEFORE])

        first_dirs = set(self.first_manager.get_dirs())
        second_dirs = set(self.second_manager.get_dirs())

        intersection_dirs = first_dirs & second_dirs
        first_to_be_removed_dirs = first_dirs - intersection_dirs
        second_to_be_removed_dirs = second_dirs - intersection_dirs
        for directory in first_to_be_removed_dirs:
            self.first_manager.remove_dir(directory=directory)

        for directory in second_to_be_removed_dirs:
            self.second_manager.remove_dir(directory=directory)

        for directory in intersection_dirs:
            self.first_manager.dive_into_dir(directory)
            self.second_manager.dive_into_dir(directory)
            self.dir_list.append(directory)
            self.__keep_syncronized__()
            self.dir_list.pop()
            self.first_manager.leave_dir()
            self.second_manager.leave_dir()

    def keep_syncronized(self):
        while True:
            self.__keep_syncronized__()
            self.first_manager.refresh()
            self.second_manager.refresh()

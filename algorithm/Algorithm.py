import logging
import os.path
import time
from collections import defaultdict

from storage.implementations.FtpFileManager import FtpFileManager
from storage.interfaces.FileManager import FileManager

BEFORE = "before"
ACTUAL = "actual"

FIRST = 1
SECOND = 2


class InitAlgorithm:
    def __init__(self, first_manager: FileManager, second_manager: FileManager):
        self.first_manager, self.second_manager = first_manager, second_manager
        self.tmp_file = 'tmp.file'
        self.is_first_level = True
        self.dir_list = list()
        self.first_snapshot = defaultdict(lambda: dict())
        self.second_snapshot = defaultdict(lambda: dict())
        self.is_changed = {
            FIRST: False,
            SECOND: False
        }

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

    def syncronize_files(self):
        current_dir = self.get_current_dir()

        first_meta = self.first_manager.get_files_metadata()
        second_meta = self.second_manager.get_files_metadata()

        self.first_snapshot[current_dir] = dict(first_meta)
        self.second_snapshot[current_dir] = dict(second_meta)

        for file in first_meta:
            if file in second_meta and first_meta[file] < second_meta[file]:
                continue

            self.copy_file(file=file, first_manager=self.first_manager, second_manager=self.second_manager)
            tmp_meta = self.second_manager.get_files_metadata()
            self.second_snapshot[current_dir][file] = tmp_meta[file]
            second_meta = tmp_meta

        for file in second_meta:
            if file in first_meta and second_meta[file] < first_meta[file]:
                continue
            self.copy_file(file=file, first_manager=self.second_manager, second_manager=self.first_manager)
            tmp_meta = self.first_manager.get_files_metadata()
            self.first_snapshot[current_dir][file] = tmp_meta[file]
            first_meta = tmp_meta

    def syncronize_dirs(self):
        first_dirs = set(self.first_manager.get_dirs())
        second_dirs = set(self.second_manager.get_dirs())

        all_dirs = set(first_dirs) | set(second_dirs)
        first_to_be_added = second_dirs - first_dirs
        second_to_be_added = first_dirs - second_dirs
        for directory in first_to_be_added:
            self.first_manager.create_dir(directory)
        for directory in second_to_be_added:
            self.second_manager.create_dir(directory)
        return all_dirs

    def __run__(self):
        current_dir = self.get_current_dir()
        if current_dir == '':
            current_dir = "base dir"
        logging.info(f"Scanning dir {current_dir}")
        self.syncronize_files()
        all_dirs = self.syncronize_dirs()

        for directory in all_dirs:
            self.first_manager.dive_into_dir(directory)
            self.second_manager.dive_into_dir(directory)
            self.dir_list.append(directory)
            self.__run__()
            self.dir_list.pop()
            self.first_manager.leave_dir()
            self.second_manager.leave_dir()

    def run(self):
        self.first_manager.setup()
        logging.info("Setup for first manager succeeded")
        self.second_manager.setup()
        logging.info("Setup for second manager succeeded")
        self.__run__()

    @staticmethod
    def remove_file(file: str, manager: FileManager):
        manager.remove_file(filename=file)

    def get_current_dir(self):
        current_dir = ''
        if len(self.dir_list) > 0:
            current_dir = os.path.join(*self.dir_list)
        return current_dir

    def refresh_created_files(self, manager: FileManager, other_manager: FileManager,
                              snapshot: dict, other_snapshot: dict):
        current_dir = self.get_current_dir()
        meta = manager.get_files_metadata()
        logging.info(f"[Create] Current meta from dir {current_dir}: {meta}")
        snapshot_copy = dict(snapshot[current_dir])
        logging.info(f"[Create] Current snapshot from dir {current_dir}: {snapshot_copy}")
        for element in meta:
            if element in snapshot_copy:
                continue
            logging.info(f"[Create][File] {element} from dir {current_dir} to manager {other_manager}")
            self.copy_file(file=element,
                           first_manager=manager,
                           second_manager=other_manager)
            tmp_meta = other_manager.get_files_metadata()
            snapshot[current_dir][element] = meta[element]
            other_snapshot[current_dir][element] = tmp_meta[element]

    def refresh_updated_files(self,
                              snapshot: dict,
                              other_snapshot: dict,
                              manager: FileManager, other_manager: FileManager):
        current_dir = self.get_current_dir()
        snapshot_copy = dict(snapshot[current_dir])
        meta = manager.get_files_metadata()
        logging.info(f"[Update] Current meta from dir {current_dir}: {meta}")
        logging.info(f"[Update] Current snapshot copy from dir {current_dir}: {snapshot_copy}")
        for element in meta:
            if element not in snapshot_copy:
                pass

            if meta[element] != snapshot_copy[element]:
                logging.info(f"[Update][File] {element} from {current_dir} from manager {other_manager} updated")
                self.copy_file(file=element, first_manager=manager, second_manager=other_manager)
                tmp_meta = other_manager.get_files_metadata()
                other_snapshot[current_dir][element] = tmp_meta[element]
                snapshot[current_dir][element] = meta[element]

    def refresh_deleted_files(self, snapshot: dict, other_snapshot: dict,
                              manager: FileManager, other_manager: FileManager, delete_index: int):
        current_dir = self.get_current_dir()
        meta = manager.get_files_metadata()
        logging.info(f"[Delete] Current meta from dir {current_dir}: {meta}")
        snapshot_copy = dict(snapshot[current_dir])
        logging.info(f"[Delete] Current snapshot copy from dir {current_dir}: {snapshot_copy}")
        for element in snapshot_copy:
            if element in meta:
                continue

            self.is_changed[delete_index] = True
            logging.info(f"[Delete][File] {element} from {other_manager}")
            other_manager.remove_file(filename=element)
            del snapshot[current_dir][element]
            del other_snapshot[current_dir][element]
        other_manager.refresh()

    def refresh_files(self):
        self.refresh_deleted_files(snapshot=self.first_snapshot, other_snapshot=self.second_snapshot,
                                   manager=self.first_manager, other_manager=self.second_manager, delete_index=SECOND)

        self.refresh_deleted_files(snapshot=self.second_snapshot, other_snapshot=self.first_snapshot,
                                   manager=self.second_manager, other_manager=self.first_manager, delete_index=FIRST)

        self.refresh_created_files(manager=self.first_manager, other_manager=self.second_manager,
                                   snapshot=self.first_snapshot, other_snapshot=self.second_snapshot)

        self.refresh_created_files(manager=self.second_manager, other_manager=self.first_manager,
                                   snapshot=self.second_snapshot, other_snapshot=self.first_snapshot)

        self.refresh_updated_files(snapshot=self.first_snapshot, other_snapshot=self.second_snapshot,
                                   manager=self.first_manager, other_manager=self.second_manager)

        self.refresh_updated_files(snapshot=self.second_snapshot, other_snapshot=self.first_snapshot,
                                   manager=self.second_manager, other_manager=self.first_manager)

    def refresh_dirs(self):
        first_dirs = set(self.first_manager.get_dirs())
        second_dirs = set(self.second_manager.get_dirs())

        intersection_dirs = first_dirs & second_dirs
        delta_first = first_dirs - intersection_dirs
        delta_second = second_dirs - intersection_dirs
        #
        # for directory in delta_first:
        #     self.first_manager.remove_dir(directory=directory)
        #     del self.first_snapshot[current_dir]
        #
        # for directory in delta_second:
        #     self.second_manager.remove_dir(directory=directory)
        #     del self.second_snapshot[current_dir]
        return intersection_dirs

    def __keep_syncronized__(self):
        self.refresh_files()
        intersection_dirs = self.refresh_dirs()

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
            self.is_changed = {
                FIRST: False,
                SECOND: False
            }
            self.__keep_syncronized__()
            # logging.info(f"Is changed status {self.is_changed}")
            if self.is_changed[FIRST]:
                self.first_manager.refresh()
            if self.is_changed[SECOND]:
                self.second_manager.refresh()
            time.sleep(1)

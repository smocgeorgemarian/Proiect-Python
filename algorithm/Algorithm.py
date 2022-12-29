import logging
import time
from collections import defaultdict

from storage.implementations.FtpFileManager import FtpFileManager
from storage.implementations.ZipFileManager import ZipFileManager
from storage.interfaces.FileManager import FileManager, FOLDERS, FILES

BEFORE = "before"
ACTUAL = "actual"

FIRST = 0
SECOND = 1
MAN_SIZE = 1


class InitAlgorithm:
    def __init__(self, mans: list[FileManager], tmp_file: str = 'tmp.file'):
        self.mans = mans
        self.snaps = [
            {
                FOLDERS: defaultdict(lambda: dict()),
                FILES: defaultdict(lambda: dict())
            },
            {
                FOLDERS: defaultdict(lambda: dict()),
                FILES: defaultdict(lambda: dict())
            }
        ]
        self.tmp_file = tmp_file

    def copy_file(self, path_data: tuple, src: FileManager, dest: FileManager, dest_meta: dict) -> None:
        if isinstance(src, FtpFileManager) \
                and isinstance(dest, FtpFileManager):
            with open(self.tmp_file, 'wb') as fd:
                src.retrieve_file(path_data, fd)
            with open(self.tmp_file, 'rb') as fd:
                dest.save_file(path_data, fd)

        elif isinstance(src, FtpFileManager):
            if isinstance(dest, ZipFileManager) and path_data in dest_meta:
                dest.remove_file(path_data)
                dest.refresh()
            fd = dest.open(path_data=path_data, mode='w')
            src.retrieve_file(path_data=path_data, fd_dest=fd)
            dest.close(fd=fd)
        else:
            if isinstance(dest, ZipFileManager) and path_data in dest_meta:
                dest.remove_file(path_data)
                dest.refresh()
            fd = src.open(path_data=path_data, mode='r')
            dest.save_file(path_data=path_data, fd_source=fd)
            src.close(fd=fd)

    def initialise(self):
        metas = [man.get_files_metadata() for man in self.mans]
        self.snaps = [dict(meta) for meta in metas]

        # compute a common format
        for man_index, meta in enumerate(metas):
            other_man_index = MAN_SIZE - man_index
            man, other_man = self.mans[man_index], self.mans[other_man_index]

            dir_snap, files_snap = self.snaps[man_index][FOLDERS], self.snaps[man_index][FILES]
            dir_meta, files_meta = meta[FOLDERS], meta[FILES]

            other_dir_meta, other_files_meta = metas[other_man_index][FOLDERS], metas[other_man_index][FILES]
            other_dir_snap, other_files_snap = self.snaps[other_man_index][FOLDERS], self.snaps[other_man_index][FILES]

            for path_data in dir_meta:
                if path_data not in other_dir_meta:
                    other_man.create_dir(path_data=path_data)
                    other_dir_snap[path_data] = None

            for path_data in files_meta:
                # if it is not newer we do not proceed
                if path_data in other_files_meta and files_meta[path_data] <= other_files_meta[path_data]:
                    continue
                other_man.mkdirs(path_data[:-1])
                self.copy_file(path_data=path_data, src=man, dest=other_man, dest_meta=other_files_meta)
                # update in memory
                files_snap[path_data] = man.get_files_metadata()[FILES][path_data]
                other_files_snap[path_data] = other_man.get_files_metadata()[FILES][path_data]

    def keep_deleted(self):
        metas = [man.get_files_metadata() for man in self.mans]
        are_changes_done = False
        for man_index, meta in enumerate(metas):
            meta_keys = set(meta.keys())
            snap = self.snaps[man_index]
            snap_keys = set(snap.keys())

            to_be_del = snap_keys - meta_keys
            other_man_index = MAN_SIZE - man_index
            other_man = self.mans[other_man_index]
            other_snap = self.snaps[other_man_index]
            for path_data in to_be_del:
                other_man.remove_file(path_data)
                if path_data in other_snap:
                    are_changes_done = True
                    del other_snap[path_data]
                if path_data in snap:
                    are_changes_done = True
                    del snap[path_data]
            other_man.refresh()
        return are_changes_done

    def keep_created(self):
        metas = [man.get_files_metadata() for man in self.mans]
        are_changes_done = False
        for man_index, meta in enumerate(metas):
            man = self.mans[man_index]
            meta_keys = set(meta.keys())
            snap = self.snaps[man_index]
            snap_keys = set(snap.keys())

            to_be_added = meta_keys - snap_keys
            other_man_index = MAN_SIZE - man_index
            other_man = self.mans[other_man_index]
            other_meta = metas[other_man_index]
            other_snap = self.snaps[other_man_index]
            for path_data in to_be_added:
                logging.info("File copied")
                self.copy_file(path_data=path_data, src=man, dest=other_man, dest_meta=other_meta)
                snap[path_data] = man.get_files_metadata()[path_data]
                other_snap[path_data] = other_man.get_files_metadata()[path_data]
                are_changes_done = True
        return are_changes_done

    def keep_updated(self):
        metas = [man.get_files_metadata() for man in self.mans]
        are_changes_done = False
        for man_index, meta in enumerate(metas):
            man = self.mans[man_index]
            meta_keys = set(meta.keys())
            snap = self.snaps[man_index]
            snap_keys = set(snap.keys())

            to_be_checked = meta_keys & snap_keys
            other_man_index = MAN_SIZE - man_index
            other_man = self.mans[other_man_index]
            other_meta = metas[other_man_index]
            other_snap = self.snaps[other_man_index]
            for path_data in to_be_checked:
                if meta[path_data] == snap[path_data]:
                    continue
                logging.info("File updated")
                self.copy_file(path_data=path_data, src=man, dest=other_man, dest_meta=other_meta)
                snap[path_data] = man.get_files_metadata()[path_data]
                meta[path_data] = snap[path_data]
                other_snap[path_data] = other_man.get_files_metadata()[path_data]
                other_meta[path_data] = other_snap[path_data]
                are_changes_done = True
        return are_changes_done

    def keep_sync(self):
        if self.keep_deleted():
            return
        if self.keep_created():
            return
        self.keep_updated()

    def run(self):
        for man in self.mans:
            man.setup()
            logging.info(f"Setup succeded for {man}")
        self.initialise()
        # while True:
        #     self.keep_sync()
        #     time.sleep(1)

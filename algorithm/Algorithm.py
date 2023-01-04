import logging
from collections import defaultdict

from storage.implementations.FtpFileManager import FtpFileManager
from storage.implementations.ZipFileManager import ZipFileManager
from storage.interfaces.FileManager import FileManager
from storage.model.PathData import PathData

BEFORE = "before"
ACTUAL = "actual"

MAN_SIZE = 1


class Algorithm:
    """
    Class used for applying continuously syncing between 2 locations

    Attributes
    ----------
    mans : tuple
        File managers used to apply files operations on storage locations
    snaps : list
        Snapshots of storage locations used to see whether changes are done
        to a specific storage location
    tmp_file : str
        Temporary file used to transfer from one location to another
        when transferring directly is not supported (e.g. ftp-ftp)
    """

    def __init__(self, mans: tuple, tmp_file: str = 'tmp.file'):
        """
        Parameters
        ----------
        mans : tuple
            Input file managers, typically constructed via
            ~storage.config.FileManagerConfigurator.FileManagerConfigurator
        tmp_file : str
            Name of the file used for transfers that need intermediary storage,
            (default is tmp.file)
        """
        self.mans = mans
        self.snaps = [
            defaultdict(lambda: dict()),
            defaultdict(lambda: dict())
        ]
        self.tmp_file = tmp_file

    def copy_file(self, path_data: PathData, src: FileManager, dest: FileManager, dest_meta: dict) -> None:
        if isinstance(src, FtpFileManager) and isinstance(dest, FtpFileManager):
            with open(self.tmp_file, 'wb') as fd:
                src.retrieve_file(path_data.path_data, fd)
            with open(self.tmp_file, 'rb') as fd:
                dest.save_file(path_data.path_data, fd)

        elif isinstance(src, FtpFileManager):
            if isinstance(dest, ZipFileManager) and path_data in dest_meta:
                dest.remove_file(path_data.path_data)
                dest.refresh()

            fd = dest.open(path_data=path_data.path_data, mode='w')
            src.retrieve_file(path_data=path_data.path_data, fd_dest=fd)
            dest.close(fd=fd)
        else:
            if isinstance(dest, ZipFileManager) and path_data in dest_meta:
                dest.remove_file(path_data.path_data)
                dest.refresh()
            fd = src.open(path_data=path_data.path_data, mode='r')
            dest.save_file(path_data=path_data.path_data, fd_source=fd)
            src.close(fd=fd)

    def initialise(self):
        try:
            metas = [man.get_files_metadata() for man in self.mans]
        except Exception as e:
            logging.error(f"Could not get files metadata. Cause of error: {str(e)}")
            return
        self.snaps = [dict(meta) for meta in metas]
        # compute a common format
        for man_index, meta in enumerate(metas):
            other_man_index = MAN_SIZE - man_index
            man, other_man = self.mans[man_index], self.mans[other_man_index]
            snap, other_snap = self.snaps[man_index], self.snaps[other_man_index]
            other_meta = metas[other_man_index]

            dirs = list(filter(lambda x: not x.is_file, meta.keys()))
            logging.info(f"Dirs of {man}: {dirs}")
            files = list(filter(lambda x: x.is_file, meta.keys()))
            logging.info(f"Files of {man}: {files}")

            for path_data in dirs:
                if path_data not in other_meta:
                    try:
                        other_man.create_dir(path_data=path_data.path_data)
                        other_snap[path_data] = None
                    except Exception as e:
                        logging.error(f"Could not create dir with path data: {path_data}. Cause of error: {str(e)}")

            for path_data in files:
                # if it is not newer we do not proceed
                if path_data in other_meta and meta[path_data] <= other_meta[path_data]:
                    continue

                try:
                    other_man.mkdirs(path_data.path_data[:-1])
                    self.copy_file(path_data=path_data, src=man, dest=other_man, dest_meta=other_meta)

                    snap[path_data] = man.get_files_metadata()[path_data]
                    other_snap[path_data] = other_man.get_files_metadata()[path_data]
                except Exception as e:
                    logging.error(f"Could not copy file from manager {man} to {other_man}. Cause of error: {str(e)}")

    def keep_deleted(self):
        try:
            metas = [man.get_files_metadata() for man in self.mans]
        except Exception as e:
            logging.error(f"Could not get files metadata. Cause of error: {str(e)}")
            return True

        are_changes_done = False
        for man_index, meta in enumerate(metas):
            other_man_index = MAN_SIZE - man_index
            other_man = self.mans[other_man_index]

            snap, other_snap = self.snaps[man_index], self.snaps[other_man_index]

            to_be_del = sorted(set(snap.keys()) - set(meta.keys()),
                               key=lambda x: (not x.is_file, -len(x.path_data)))

            for path_data in to_be_del:
                try:
                    if path_data.is_file:
                        other_man.remove_file(path_data.path_data)
                    else:
                        other_man.remove_dir(path_data.path_data)

                    if path_data in other_snap:
                        are_changes_done = True
                        del other_snap[path_data]
                    if path_data in snap:
                        are_changes_done = True
                        del snap[path_data]
                except Exception as e:
                    logging.error(f"Could not delete object {path_data}. Cause of error: {str(e)}")
            try:
                other_man.refresh()
            except Exception as e:
                logging.error(f"Could not refresh manager: {other_man}. Cause of error: {str(e)}")
                return True
        return are_changes_done

    def keep_created(self):
        try:
            metas = [man.get_files_metadata() for man in self.mans]
        except Exception as e:
            logging.error(f"Could not get files metadata. Cause of error: {str(e)}")
            return True

        are_changes_done = False
        for man_index, meta in enumerate(metas):
            other_man_index = MAN_SIZE - man_index
            other_meta = metas[other_man_index]

            man, other_man = self.mans[man_index], self.mans[other_man_index]
            logging.info(f"Current meta: {meta}")
            snap, other_snap = self.snaps[man_index], self.snaps[other_man_index]
            logging.info(f"Current snap: {snap}")
            to_be_added = sorted(set(meta.keys()) - set(snap.keys()), key=lambda x: (not x.is_file, len(x.path_data)))
            for path_data in to_be_added:
                try:
                    if not path_data.is_file:
                        other_man.create_dir(path_data.path_data)
                    else:
                        self.copy_file(path_data=path_data, src=man, dest=other_man, dest_meta=other_meta)
                    new_data = man.get_files_metadata()[path_data]
                    other_new_data = other_man.get_files_metadata()[path_data]
                except Exception as e:
                    logging.error(f"Could not create object {path_data}. Cause of error: {str(e)}")
                    continue

                snap[path_data] = new_data
                other_snap[path_data] = other_new_data
                other_meta[path_data] = other_new_data

        return are_changes_done

    def keep_updated(self):
        try:
            metas = [man.get_files_metadata() for man in self.mans]
        except Exception as e:
            logging.error(f"Could not get files metadata. Cause of error: {str(e)}")
            return True
        are_changes_done = False
        for man_index, meta in enumerate(metas):
            other_man_index = MAN_SIZE - man_index
            other_meta = metas[other_man_index]

            man, other_man = self.mans[man_index], self.mans[other_man_index]
            logging.info(f"Current meta: {meta}")
            snap, other_snap = self.snaps[man_index], self.snaps[other_man_index]
            logging.info(f"Current snap: {snap}")
            to_be_checked = list(filter(lambda x: x.is_file,
                                        set(meta.keys()) & set(snap.keys())))
            for path_data in to_be_checked:
                if meta[path_data] == snap[path_data]:
                    continue
                try:
                    self.copy_file(path_data=path_data, src=man, dest=other_man, dest_meta=other_meta)
                    new_data = man.get_files_metadata()[path_data]
                    other_new_data = other_man.get_files_metadata()[path_data]
                except Exception as e:
                    logging.error(f"Could not update object {path_data}. Cause of error: {str(e)}")
                    continue

                snap[path_data] = new_data
                other_snap[path_data] = other_new_data
                other_meta[path_data] = other_new_data
        return are_changes_done

    def keep_sync(self):
        if self.keep_deleted():
            return
        if self.keep_created():
            return
        self.keep_updated()

    def run(self):
        for man in self.mans:
            try:
                man.setup()
            except Exception as e:
                logging.error(f"Setup failed for manager: {man}. Cause of error: {str(e)}")
                return
            logging.info(f"Setup succeeded for {man}")
        self.initialise()
        while True:
            self.keep_sync()

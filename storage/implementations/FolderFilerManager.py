import os
import shutil
from pathlib import Path
from typing import BinaryIO

from storage.interfaces.FileManager import FileManager, FOLDERS, FILES

BUFFER_SIZE = 8096


class FolderFileManager(FileManager):
    def mkdirs(self, dirs: list[str]) -> None:
        full_path = os.path.join(self.path, *dirs)
        os.makedirs(full_path, exist_ok=True)

    def close(self, fd: BinaryIO) -> None:
        fd.close()

    def __init__(self, conn_string: str):
        super().__init__(conn_string)
        self.path = conn_string
        self.metadata = dict()
        self.current_dirs = []

    def dive_into_dir(self, child_dir: str):
        if os.path.exists(os.path.join(self.path, *self.current_dirs, child_dir)):
            self.current_dirs.append(child_dir)

    def leave_current_dir(self):
        self.current_dirs.pop()

    def setup(self):
        pass

    def open(self, path_data: tuple, mode='r'):
        full_file_path = os.path.join(self.path, *path_data)
        return open(full_file_path, mode + 'b')

    def retrieve_file(self, path_data, fd_dest):
        pass

    def save_file(self, path_data: tuple, fd_source):
        full_file_path = os.path.join(self.path, *path_data)
        with open(full_file_path, mode='wb') as fd:
            while True:
                content = fd_source.read(BUFFER_SIZE)
                if content == b'':
                    break
                fd.write(content)

    def leave_dir(self):
        self.current_dirs.pop()

    def get_files_metadata(self):
        return_meta = {
            FOLDERS: dict(),
            FILES: dict()
        }
        prefix_size = len(Path(self.path).parts)

        for root, dirs, files in os.walk(self.path, topdown=False):
            path_obj = Path(root)
            path_dir_data = list(path_obj.parts[prefix_size:])

            for directory in dirs:
                path_data = tuple([*path_dir_data, directory])
                return_meta[FOLDERS][path_data] = None

            for file in files:
                file_full_path = os.path.join(root, file)
                path_data = tuple([*path_dir_data, file])
                return_meta[FILES][path_data] = os.stat(file_full_path).st_mtime

        return return_meta

    def get_dirs(self):
        full_root_path = os.path.join(self.path, *self.current_dirs)
        return [maybe_dir for maybe_dir in os.listdir(full_root_path)
                if os.path.isdir(os.path.join(full_root_path, maybe_dir))]

    def create_dir(self, path_data: tuple):
        full_dir_path = os.path.join(self.path, *path_data)
        os.makedirs(full_dir_path, exist_ok=True)

    def remove_dir(self, path_data: tuple):
        full_dir_path = os.path.join(self.path, *path_data)
        shutil.rmtree(full_dir_path)

    def remove_file(self, path_data: tuple):
        full_file_path = os.path.join(self.path, *path_data)
        os.remove(full_file_path)

    def refresh(self):
        pass

    def __str__(self):
        return "Folder file manager"

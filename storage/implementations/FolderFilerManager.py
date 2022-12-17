import os
import shutil
from typing import BinaryIO

from storage.interfaces.FileManager import FileManager

BUFFER_SIZE = 8096


class FolderFileManager(FileManager):
    def close(self, fd: BinaryIO) -> None:
        pass

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

    def open(self, filename, mode='r'):
        full_file_path = os.path.join(self.path, *self.current_dirs, filename)
        return open(full_file_path, mode + 'b')

    def retrieve_file(self, filename, fd_dest):
        pass

    def save_file(self, filename, fd_source):
        full_file_path = os.path.join(self.path, *self.current_dirs, filename)
        with open(full_file_path, mode='wb') as fd:
            while True:
                content = fd_source.read(BUFFER_SIZE)
                if content == b'':
                    break
                fd.write(content)

    def leave_dir(self):
        self.current_dirs.pop()

    def get_files_metadata(self):
        full_root_path = os.path.join(self.path, *self.current_dirs)
        metadata = dict()
        for maybe_file in os.listdir(full_root_path):
            actual_path = os.path.join(full_root_path, maybe_file)
            if os.path.isfile(actual_path):
                metadata[maybe_file] = os.stat(actual_path).st_mtime
        return metadata

    def get_dirs(self):
        full_root_path = os.path.join(self.path, *self.current_dirs)
        return [maybe_dir for maybe_dir in os.listdir(full_root_path)
                if os.path.isdir(os.path.join(full_root_path, maybe_dir))]

    def create_dir(self, directory):
        full_dir_path = os.path.join(self.path, *self.current_dirs, directory)
        os.makedirs(full_dir_path)

    def remove_dir(self, directory):
        full_dir_path = os.path.join(self.path, *self.current_dirs, directory)
        shutil.rmtree(full_dir_path)

    def remove_file(self, filename):
        full_file_path = os.path.join(self.path, *self.current_dirs, filename)
        os.remove(full_file_path)

    def refresh(self):
        pass

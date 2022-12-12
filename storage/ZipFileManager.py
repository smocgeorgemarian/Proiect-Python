import os
import zipfile
from datetime import datetime
from pathlib import PurePath
from typing import Literal

from storage.FileManager import FileManager

SEPARATOR = "/"

BUFFER_SIZE = 8096


class ZipFileManager(FileManager):
    def __init__(self, conn_string: str):
        super().__init__(conn_string)
        self.path = conn_string
        self.zip = zipfile.ZipFile(self.path)
        self.current_dirs = []
        self.black_list = []

    def setup(self):
        self.zip = zipfile.ZipFile(self.path)

    @staticmethod
    def to_mili_from_epoch(date_time):
        return (datetime(date_time[0], month=date_time[1], day=date_time[2], hour=date_time[3], minute=date_time[4],
                         second=date_time[5]) - datetime(1970, month=1, day=1)).total_seconds()

    def is_file_in_current_dir(self, maybe_file):
        if maybe_file.endswith(SEPARATOR):
            return False

        current_dir_full_path = SEPARATOR.join(self.current_dirs)
        if current_dir_full_path != '':
            current_dir_full_path += SEPARATOR
        if not maybe_file.startswith(current_dir_full_path):
            return False

        relative_name = maybe_file[len(current_dir_full_path):]
        if relative_name.count(SEPARATOR) > 0:
            return False
        return True

    def get_simple_name(self, filename):
        current_dir_full_path = SEPARATOR.join(self.current_dirs)
        if current_dir_full_path != '':
            current_dir_full_path += SEPARATOR
        return filename[len(current_dir_full_path):]

    def get_files_metadata(self):
        return {self.get_simple_name(file_meta.filename): self.to_mili_from_epoch(file_meta.date_time)
                for file_meta in self.zip.infolist()
                if self.is_file_in_current_dir(file_meta.filename)}

    def retrieve_file(self, filename, fd_dest):
        with zipfile.ZipFile(self.path, mode='r') as zip_fd:
            with zip_fd.open(filename, mode='r') as fd:
                while True:
                    content = fd.read(BUFFER_SIZE)
                    if content == '':
                        break
                    fd_dest.write(content)

    def save_file(self, filename, fd_source):
        full_file_path = PurePath.joinpath(*self.current_dirs, filename)
        with zipfile.ZipFile(self.path, mode='a') as zip_fd:
            with zip_fd.open(full_file_path, mode='w') as fd:
                while True:
                    content = fd_source.read(BUFFER_SIZE)
                    if content == b'':
                        break
                    fd.write(content)

    def open(self, filename, mode: Literal['r', 'w'] = 'r'):
        full_file_path = os.path.join(*self.current_dirs, filename)
        if mode == 'w':
            return zipfile.ZipFile(self.path, mode='a').open(name=full_file_path, mode=mode)
        return zipfile.ZipFile(self.path, mode=mode).open(name=full_file_path, mode=mode)

    @staticmethod
    def get_next_chunk(fd):
        return fd.read(BUFFER_SIZE)

    def dive_into_dir(self, directory):
        self.current_dirs.append(directory)

    def leave_dir(self):
        self.current_dirs.pop()

    def is_dir_in_current_dir(self, maybe_dir: str):
        # edge case
        if maybe_dir == '':
            return

        if len(self.current_dirs) > 0:
            current_dir_full_path = os.path.join(*self.current_dirs)
        else:
            current_dir_full_path = ''

        parent_dir = os.path.dirname(maybe_dir)
        return current_dir_full_path == parent_dir

    def get_dirs(self):
        dirs = list(filter(lambda x: self.is_dir_in_current_dir(x), set([os.path.dirname(x)
                                                                         for x in self.zip.namelist()])))
        dirs = list(map(lambda x: os.path.basename(x), dirs))
        return dirs

    def create_dir(self, directory):
        pass

    def remove_dir(self, directory):
        full_path_dir = os.path.join(*self.current_dirs, directory)
        self.black_list.append(full_path_dir)

    def remove_file(self, filename):
        full_path_file = os.path.join(*self.current_dirs, filename)
        self.black_list.append(full_path_file)

    def refresh(self):
        tmp_zip = zipfile.ZipFile(self.path + "tmp", mode='w')
        for file_meta in self.zip.infolist():
            if file_meta.filename in self.black_list:
                continue

            if file_meta.filename.endswith(SEPARATOR):
                continue

            with zipfile.ZipFile(self.path, mode='r') as zip_fd:
                with zip_fd.open(name=file_meta.filename, mode='r') as fd:

                    with zipfile.ZipFile(self.path + "tmp", mode='a') as tmp_zip_fd:
                        with tmp_zip_fd.open(name=file_meta.filename, mode='w') as tmp_fd:
                            while True:
                                content = fd.read(BUFFER_SIZE)
                                if content == b'':
                                    break
                                tmp_fd.write(content)

        self.black_list = []

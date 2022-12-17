import os
import zipfile
from datetime import datetime
from pathlib import PurePath
from typing import Literal, BinaryIO, IO

from storage.interfaces.FileManager import FileManager

SEPARATOR = "/"

BUFFER_SIZE = 8096


class ZipFileManager(FileManager):
    def close(self, fd: BinaryIO) -> None:
        fd.close()
        self.last_man_opened_zip.close()

    def __init__(self, conn_string: str) -> None:
        super().__init__(conn_string)
        self.last_man_opened_zip = None
        self.path = conn_string
        self.zip = None
        self.current_dirs = []
        self.black_list = []

    def setup(self) -> None:
        the_zipfile = zipfile.ZipFile(self.path)
        try:
            the_zipfile.testzip()
            the_zipfile.close()
        except zipfile.BadZipFile as e:
            raise Exception("Zip File is not valid") from e

    @staticmethod
    def to_millis_from_epoch(date_time: tuple) -> float:
        return (datetime(date_time[0], month=date_time[1], day=date_time[2], hour=date_time[3], minute=date_time[4],
                         second=date_time[5]) - datetime(1970, month=1, day=1)).total_seconds()

    def is_file_in_current_dir(self, maybe_file: str) -> bool:
        if maybe_file.endswith(SEPARATOR):
            return False

        if len(self.current_dirs) > 0:
            current_dir_full_path = os.path.join(*self.current_dirs)
        else:
            current_dir_full_path = ''
        maybe_file_parent_dir = os.path.dirname(maybe_file)
        return current_dir_full_path == maybe_file_parent_dir

    def get_files_metadata(self) -> dict:
        with zipfile.ZipFile(self.path) as tmp_zip:
            return {self.get_simple_name(file_meta.filename):
                    self.to_millis_from_epoch(file_meta.date_time)
                    for file_meta in tmp_zip.infolist()
                    if self.is_file_in_current_dir(file_meta.filename)}

    def retrieve_file(self, filename: str, fd_dest: BinaryIO) -> None:
        with zipfile.ZipFile(self.path, mode='r') as zip_fd:
            with zip_fd.open(filename, mode='r') as fd:
                while True:
                    content = fd.read(BUFFER_SIZE)
                    if content == '':
                        break
                    fd_dest.write(content)

    def save_file(self, filename: str, fd_source: IO[bytes]) -> None:
        full_file_path = os.path.join(*self.current_dirs, filename)
        with zipfile.ZipFile(self.path, mode='a') as zip_fd:
            with zip_fd.open(full_file_path, mode='w') as fd:
                while True:
                    content = fd_source.read(BUFFER_SIZE)
                    if content == b'':
                        break
                    fd.write(content)

    def open(self, filename, mode: Literal['r', 'w'] = 'r') -> IO[bytes]:
        full_file_path = SEPARATOR.join([*self.current_dirs, filename])
        if mode == 'w':
            zip_file_mode = 'a'
        else:
            zip_file_mode = 'r'

        self.last_man_opened_zip = zipfile.ZipFile(self.path, mode=zip_file_mode)
        return self.last_man_opened_zip.open(name=full_file_path, mode=mode)

    def dive_into_dir(self, directory: str) -> None:
        self.current_dirs.append(directory)

    def leave_dir(self) -> None:
        self.current_dirs.pop()

    def is_dir_in_current_dir(self, maybe_dir: str) -> bool:
        if maybe_dir == '':
            return False

        if len(self.current_dirs) > 0:
            current_dir_full_path = os.path.join(*self.current_dirs)
        else:
            current_dir_full_path = ''

        parent_dir = os.path.dirname(maybe_dir)
        return current_dir_full_path == parent_dir

    def get_dirs(self) -> list[str]:
        with zipfile.ZipFile(self.path) as tmp_zip:
            dirs = list(filter(lambda x: self.is_dir_in_current_dir(x), set([os.path.dirname(x)
                                                                             for x in tmp_zip.namelist()])))
            dirs = list(map(lambda x: os.path.basename(x), dirs))
        return dirs

    def create_dir(self, directory: str) -> None:
        pass

    def remove_dir(self, directory: str) -> None:
        full_path_dir = os.path.join(*self.current_dirs, directory)
        self.black_list.append(full_path_dir)

    def remove_file(self, filename: str) -> None:
        full_path_file = os.path.join(*self.current_dirs, filename)
        self.black_list.append(full_path_file)

    def refresh(self) -> None:
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

    @staticmethod
    def get_simple_name(filename: str) -> str:
        return PurePath(filename).name

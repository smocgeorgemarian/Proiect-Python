import logging
import os
import zipfile
from datetime import datetime
from pathlib import PurePath, Path
from typing import Literal, BinaryIO, IO

from storage.interfaces.FileManager import FileManager, FOLDERS, FILES

TMP_SUFFIX = ".tmp"

SEPARATOR = "/"

BUFFER_SIZE = 8096


class ZipFileManager(FileManager):
    def mkdirs(self, dirs: list[str]) -> None:
        pass

    def close(self, fd: BinaryIO) -> None:
        fd.close()
        self.last_man_opened_zip.close()

    def __init__(self, conn_string: str) -> None:
        super().__init__(conn_string)
        self.last_man_opened_zip = None
        self.path = conn_string.split("zip:")[1]
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

    def get_current_dir(self) -> str:
        if len(self.current_dirs) > 0:
            current_dir = SEPARATOR.join(self.current_dirs)
        else:
            current_dir = ''
        return current_dir

    def get_path_data(self, filename):
        return tuple(Path(filename).parts)

    def is_file_in_current_dir(self, maybe_file: str) -> bool:
        if maybe_file.endswith(SEPARATOR):
            return False
        current_dir = self.get_current_dir()
        maybe_file_parent_dir = os.path.dirname(maybe_file)
        return current_dir == maybe_file_parent_dir

    def get_files_metadata(self) -> dict:
        data = {
            FOLDERS: dict(),
            FILES: dict()
        }
        with zipfile.ZipFile(self.path) as tmp_zip:
            brute_infolist = tmp_zip.infolist()

            for file_meta in brute_infolist:
                path_data = self.get_path_data(file_meta.filename)
                if file_meta.is_dir():
                    data[FOLDERS][path_data] = None
                else:
                    data[FILES][path_data] = self.to_millis_from_epoch(file_meta.date_time)
        return data

    def retrieve_file(self, path_data: tuple, fd_dest: BinaryIO) -> None:
        full_file_path = SEPARATOR.join(path_data)
        with zipfile.ZipFile(self.path, mode='r') as zip_fd:
            with zip_fd.open(full_file_path, mode='r') as fd:
                while True:
                    content = fd.read(BUFFER_SIZE)
                    if content == '':
                        break
                    fd_dest.write(content)

    def save_file(self, path_data: str, fd_source: IO[bytes]) -> None:
        full_file_path = SEPARATOR.join(path_data)
        with zipfile.ZipFile(self.path, mode='a') as zip_fd:
            with zip_fd.open(full_file_path, mode='w') as fd:
                while True:
                    content = fd_source.read(BUFFER_SIZE)
                    if content == b'':
                        break
                    fd.write(content)

    def open(self, path_data: tuple, mode: Literal['r', 'w'] = 'r') -> IO[bytes]:
        full_file_path = SEPARATOR.join(path_data)
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
            current_dir_full_path = SEPARATOR.join(self.current_dirs)
        else:
            current_dir_full_path = ''

        parent_dir = os.path.dirname(maybe_dir)
        return current_dir_full_path == parent_dir

    def get_dirs(self) -> list[str]:
        dirs = set()
        with zipfile.ZipFile(self.path) as tmp_zip:
            non_empty_dirs = set(os.path.dirname(element)
                                 for element in tmp_zip.namelist())

            for non_empty_dir in non_empty_dirs:
                rec_dirs = {non_empty_dir}
                parent_dir = os.path.dirname(non_empty_dir)
                while parent_dir != non_empty_dir and parent_dir != '':
                    rec_dirs.add(parent_dir)
                    non_empty_dir = parent_dir
                    parent_dir = os.path.dirname(non_empty_dir)
                dirs |= rec_dirs
        values = list(map(lambda x: os.path.basename(x),
                          list(filter(lambda x: self.is_dir_in_current_dir(x), dirs))))
        return values

    def create_dir(self, path_data: tuple) -> None:
        full_dir_path = SEPARATOR.join(path_data) + SEPARATOR
        zfi = zipfile.ZipInfo(full_dir_path)
        with zipfile.ZipFile(self.path, mode='a') as zip_fd:
            zip_fd.writestr(zfi, '')

    def remove_dir(self, path_data: tuple) -> None:
        self.black_list.append(path_data)

    def remove_file(self, path_data: tuple) -> None:
        full_path_file = SEPARATOR.join(path_data)
        self.black_list.append(full_path_file)

    def refresh(self) -> None:
        if not self.black_list:
            return
        logging.info(f"Current blacklist {self.black_list}")
        tmp_file_path = self.path + TMP_SUFFIX
        with zipfile.ZipFile(self.path, mode='r') as zip_fd:
            brute_infolist = zip_fd.infolist()
            brute_infolist.sort(key=lambda x: x.is_dir())

            for file_meta in brute_infolist:
                if file_meta.filename in self.black_list:
                    continue

                if file_meta.is_dir():
                    with zipfile.ZipFile(tmp_file_path, mode='a') as tmp_zip_fd:
                        zfi = zipfile.ZipInfo(filename=file_meta.filename)
                        tmp_zip_fd.writestr(zfi, '')
                    continue

                with zip_fd.open(name=file_meta.filename, mode='r') as fd:
                    with zipfile.ZipFile(tmp_file_path, mode='a') as tmp_zip_fd:
                        with tmp_zip_fd.open(name=file_meta.filename, mode='w') as tmp_fd:
                            while True:
                                content = fd.read(BUFFER_SIZE)
                                if content == b'':
                                    break
                                tmp_fd.write(content)
        status = os.stat(self.path)

        os.remove(self.path)
        os.rename(src=tmp_file_path, dst=self.path)
        os.chmod(self.path, status.st_mode)
        self.black_list = []

    @staticmethod
    def get_simple_name(filename: str) -> str:
        return PurePath(filename).name

    def __str__(self):
        return "Zip file manager"

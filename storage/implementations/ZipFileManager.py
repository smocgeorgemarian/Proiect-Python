import logging
import os
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Literal, BinaryIO, IO

from storage.interfaces.FileManager import FileManager
from storage.model.PathData import PathData

TMP_SUFFIX = ".tmp"

SEPARATOR = "/"

BUFFER_SIZE = 8096


class ZipFileManager(FileManager):
    def retrieve_file(self, path_data: tuple, fd_dest) -> None:
        pass

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
        self.black_list = set()

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

    def get_files_metadata(self) -> dict:
        data = dict()
        with zipfile.ZipFile(self.path) as tmp_zip:
            brute_infolist = tmp_zip.infolist()

            for file_meta in brute_infolist:
                path_data = self.get_path_data(filename=file_meta.filename)
                path_data_obj = PathData(path_data=path_data, is_file=not file_meta.is_dir())
                data[path_data_obj] = self.to_millis_from_epoch(file_meta.date_time)
        return data

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
        zip_file_mode = 'r'
        if mode == 'w':
            zip_file_mode = 'a'

        self.last_man_opened_zip = zipfile.ZipFile(self.path, mode=zip_file_mode)
        return self.last_man_opened_zip.open(name=full_file_path, mode=mode)

    def create_dir(self, path_data: tuple) -> None:
        logging.info(f"Creating dir: {path_data}")
        full_dir_path = SEPARATOR.join(path_data) + SEPARATOR
        zfi = zipfile.ZipInfo(full_dir_path)
        with zipfile.ZipFile(self.path, mode='a') as zip_fd:
            zip_fd.writestr(zfi, '')

    def remove_dir(self, path_data: tuple) -> None:
        self.black_list.add(path_data)

    def remove_file(self, path_data: tuple) -> None:
        self.black_list.add(path_data)

    def refresh(self) -> None:
        if not self.black_list:
            return
        logging.info(f"Current blacklist {self.black_list}")
        tmp_file_path = self.path + TMP_SUFFIX
        with zipfile.ZipFile(self.path, mode='r') as zip_fd:
            brute_infolist = zip_fd.infolist()
            brute_infolist.sort(key=lambda x: x.is_dir())

            for file_meta in brute_infolist:
                data = self.get_path_data(filename=file_meta.filename)
                logging.info(f"Data: {data}")
                if data in self.black_list:
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
        self.black_list = set()

    @staticmethod
    def get_path_data(filename: str) -> tuple:
        return tuple(Path(filename).parts)

    def __str__(self) -> str:
        return "Zip file manager"

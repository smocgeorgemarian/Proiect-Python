"""
Module contains the manager for a ftp folder and methods
that it should implement as a generic FileManager. Default port,
path separator and default timeout is also set here.
"""

import logging
from datetime import datetime
from ftplib import FTP
from typing import BinaryIO
from src.storage.interfaces.FileManager import FileManager
from src.storage.model.PathData import PathData

DEFAULT_PORT = 21

DEFAULT_TIMEOUT = 30

SEPARATOR = "/"


class FtpFileManager(FileManager):
    """
    File Manager implementation for a ftp folder.
    """

    def mkdirs(self, dirs: tuple) -> None:
        prefix = '.'
        for dir_index, directory in enumerate(dirs):
            if prefix != '.':
                full_path_dir = SEPARATOR.join([prefix, directory])
            else:
                full_path_dir = directory
            data = self.ftp.nlst(prefix)
            if full_path_dir not in data:
                logging.info(f"New dir to be created: {directory}")
                self.ftp.mkd(full_path_dir)
            if prefix == '.':
                prefix = SEPARATOR.join([prefix, directory])
            else:
                prefix = full_path_dir

    def remove_file(self, path_data: tuple) -> None:
        full_path_file = SEPARATOR.join(path_data)
        self.ftp.delete(full_path_file)

    def close(self, fd: BinaryIO) -> None:
        pass

    def __init__(self, conn_string):
        super().__init__(conn_string)
        self.conn_string = conn_string
        prefix, self.user, passwd_and_host = conn_string.split(':')
        self.passwd, host_and_dir = passwd_and_host.split('@')
        if "/" not in host_and_dir:
            self.host = host_and_dir
            self.start_dir = ''
        else:
            self.host, self.start_dir = host_and_dir.split("/", maxsplit=1)

        self.ftp = FTP(timeout=DEFAULT_TIMEOUT)
        self.metadata = dict()
        self.curr_dirs = []
        self.fd_dest = None
        self.meta = dict()

    def setup(self):
        self.ftp.connect(host=self.host, port=DEFAULT_PORT)
        self.ftp.login(user=self.user, passwd=self.passwd)
        self.ftp.cwd(dirname=self.start_dir)

    def process_spaced_metadata(self, element: str) -> list:
        const_data = list(filter(lambda x: x, element.split(" ")))[:3]
        start_index = element.find(f" {const_data[2]} ")
        last_index = start_index + len(const_data[2]) + 2
        while element[last_index] == ' ':
            last_index += 1

        last_data = element[last_index:]
        const_data.append(last_data)

        full_path = list(self.curr_dirs)
        full_path.append(const_data[3])
        const_data[3] = tuple(full_path)
        return const_data

    def get_modif_date(self, path_data: tuple):
        full_file_path = SEPARATOR.join(path_data)
        modif_str = self.ftp.sendcmd(f'MDTM {full_file_path}').split(" ")[1]
        modif_date = datetime.strptime(modif_str, "%Y%m%d%H%M%S")
        epoch_date = datetime.strptime("19700101", "%Y%m%d")
        return (modif_date - epoch_date).total_seconds()

    def get_files_metadata(self, index=0):
        if index == 0:
            self.meta = dict()

        content = []
        curr_dir = ''
        if len(self.curr_dirs) != 0:
            curr_dir = SEPARATOR.join(self.curr_dirs)

        self.ftp.dir(curr_dir, content.append)
        data = [self.process_spaced_metadata(element) for element in content]
        files_data = [element for element in data if "DIR" not in element[2]]

        self.meta.update(
            {PathData(path_data=file_data[3]): self.get_modif_date(file_data[3])
             for file_data in files_data})

        dirs_data = [element for element in data if "DIR" in element[2]]
        self.meta.update({PathData(path_data=dir_data[3], is_file=False): None for dir_data in dirs_data})
        for dir_data in dirs_data:
            self.curr_dirs.append(dir_data[3][-1])
            self.get_files_metadata(index + 1)
            self.curr_dirs.pop()

        return self.meta

    def get_dirs(self):
        content = []

        self.ftp.dir('.', content.append)
        data = [self.process_spaced_metadata(element)
                for element in content]

        files_data = [element for element in data if "DIR" in element[2]]
        return [file_data[3] for file_data in files_data]

    def retrieve_file(self, path_data: tuple, fd_dest):
        full_path = SEPARATOR.join(path_data)
        self.ftp.retrbinary(f"RETR {full_path}", fd_dest.write)

    def save_file(self, path_data: tuple, fd_source):
        full_path = SEPARATOR.join(path_data)
        self.ftp.storbinary(f'STOR {full_path}', fd_source)

    def create_dir(self, path_data: tuple):
        self.mkdirs(path_data)

    def remove_dir(self, path_data):
        if len(path_data) == 1:
            full_dir_path = path_data[0]
        else:
            full_dir_path = "./" + SEPARATOR.join(path_data)
        content = self.ftp.nlst(full_dir_path)
        if not content:
            self.ftp.rmd(full_dir_path)

    def open(self, filename, mode='r'):
        return None

    def refresh(self):
        pass

    def __str__(self):
        return "Ftp file manager"

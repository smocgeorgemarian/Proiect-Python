from abc import abstractmethod
from typing import BinaryIO


class FileManager:
    def __init__(self, conn_string: str) -> None:
        self.conn_string = conn_string

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def retrieve_file(self, path_data: tuple, fd_dest) -> None:
        pass

    @abstractmethod
    def save_file(self, path_data: tuple, fd_source) -> None:
        pass

    @abstractmethod
    def dive_into_dir(self, directory: str) -> None:
        pass

    @abstractmethod
    def leave_dir(self) -> None:
        pass

    @abstractmethod
    def get_files_metadata(self) -> dict:
        pass

    @abstractmethod
    def get_dirs(self) -> list[str]:
        pass

    @abstractmethod
    def create_dir(self, path_data: tuple) -> None:
        pass

    @abstractmethod
    def remove_dir(self, directory: str) -> None:
        pass

    @abstractmethod
    def mkdirs(self, dirs: list[str]) -> None:
        pass

    @abstractmethod
    def open(self, path_data: tuple, mode: str = 'r') -> BinaryIO:
        pass

    @abstractmethod
    def close(self, fd: BinaryIO) -> None:
        pass

    @abstractmethod
    def remove_file(self, path_data: tuple) -> None:
        pass

    @abstractmethod
    def refresh(self) -> None:
        pass

    @staticmethod
    def close(fd: BinaryIO) -> None:
        fd.close()

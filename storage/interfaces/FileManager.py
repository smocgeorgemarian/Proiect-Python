from abc import abstractmethod
from typing import BinaryIO

FOLDERS = 0
FILES = 1


class FileManager:
    """
    Abstract class providing methods to be implemented for syncing a memory location

    Attributes
    ----------
    conn_string : str
        Connection string passed to the application, meant
        to be processed by each class extending this class
    """

    def __init__(self, conn_string: str) -> None:
        """"

        """
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
    def get_files_metadata(self) -> dict:
        pass

    @abstractmethod
    def create_dir(self, path_data: tuple) -> None:
        pass

    @abstractmethod
    def remove_dir(self, path_data: tuple) -> None:
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

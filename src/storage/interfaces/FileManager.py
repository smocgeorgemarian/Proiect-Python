"""
File manager interface used to define the methods for
manipulating files, such as open, close, read and write
and obtaining modification date based on which decisions
of Algorithm are made.
"""
from abc import abstractmethod
from typing import BinaryIO, Literal

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

    Methods
    -------
    setup()
        Initial setup of the class (should be connection-related)
    retrieve_file(path_data: tuple, fd_dest: BinaryIO)
        Retrieves the file, writing it at destination
    save_file(path_data: tuple, fd_source: BinaryIO)
        Saves the file at the specified source
    get_files_metadata()
        Creates a dict where keys are PathData objects and values are
        modification date and returns it
    create_dir(path_data: tuple)
        Creates a dir at specified path
    remove_dir(path_data: tuple)
        Removes dir from specified path
    mkdirs(dirs: list[str])
        Creates specified dirs sequence starting from root
    open(path_data: tuple, mode: Literal['r', 'w'] = 'r')
        Opens the file from specified path in specified mode, mapped to binary
    close(fd: BinaryIO)
        Closes the file specified via file descriptor
    remove_file(path_data: tuple):
        Removes file specified by path
    refresh()
        Refreshes the content of the storage location
    """

    def __init__(self, conn_string: str) -> None:
        """
        Parameters
        ----------
        conn_string : str
            Connection string passed to the application, meant
            to be processed by each class extending this class
        """

        self.conn_string = conn_string

    @abstractmethod
    def setup(self):
        """
        Initial setup or any sort of arranging
        """

        pass

    @abstractmethod
    def retrieve_file(self, path_data: tuple, fd_dest: BinaryIO) -> None:
        """
        Writes file specified to the destination descriptor.

        Parameters
        ----------
        path_data : tuple
            Relative path to the file, usually extracted from PathData object.
        fd_dest : BinaryIO
            File descriptor of the destination.
        """

        pass

    @abstractmethod
    def save_file(self, path_data: tuple, fd_source: BinaryIO) -> None:
        """
        Writes file specified to the storage location of current FileManager.

        Parameters
        ----------
        path_data : tuple
            Relative path where the file should be created, usually extracted from PathData object.
        fd_source : BinaryIO
            File descriptor of the source.
        """

        pass

    @abstractmethod
    def get_files_metadata(self) -> dict:
        """
        Gets the metadata of all files and folders in the current storage location.

        Parses the information about the files and folders and creates a common format,
        so they can be used in sync algorithm.

        Returns
        ----------
        dict
            Metadata stored with PathData object as key
            and modification date as value (if necessary, None otherwise)
        """

        pass

    @abstractmethod
    def create_dir(self, path_data: tuple) -> None:
        """
        Creates a dir at specified relative path

        Parameters
        ----------
        path_data : tuple
            Relative path where the dir should be created, usually extracted from PathData object.
        """

        pass

    @abstractmethod
    def remove_dir(self, path_data: tuple) -> None:
        """
        Removes a dir at specified relative path

        Parameters
        ----------
        path_data : tuple
            Relative path where the dir to be deleted is located, usually extracted from PathData object.
        """

        pass

    @abstractmethod
    def mkdirs(self, dirs: list[str]) -> None:
        """
        Creates a specified dir sequence from root.

        Silently ignores the case when one or more dirs exist, creating only
        the necessary ones.

        Parameters
        ----------
        dirs : list
            Sequence of dirs to be created (starting from root).
        """

        pass

    @abstractmethod
    def open(self, path_data: tuple, mode: Literal['r', 'w'] = 'r') -> BinaryIO:
        """
        Opens the specified file in the specified mode.

        Typically, mode is mapped to the binary equivalent for support between
        different storage types reasons.

        Parameters
        ----------
        path_data : list
            Relative path where the file to be deleted is located, usually extracted from PathData object.
        mode : Literal
            Specifies the mode in which the file should be opened, typically mapped to binary
            equivalent

        Returns
        -------
        BinaryIO
            The descriptor of the file to be used in different operations
        """

        pass

    @abstractmethod
    def close(self, fd: BinaryIO) -> None:
        """
        Closes the specified file via file descriptor.

        Parameters
        ----------
        fd : BinaryIO
            File descriptor to be closed.
        """

        pass

    @abstractmethod
    def remove_file(self, path_data: tuple) -> None:
        """
        Removes the specified file by relative path.

        Parameters
        ----------
        path_data : list
            Relative path where the file to be deleted is located, usually extracted from PathData object.
        """

        pass

    @abstractmethod
    def refresh(self) -> None:
        """
        Refreshes the content of the storage location.

        Created as an extension that permits different actions between iterations
        of sync algorithm. Currently, used for zip only.
        """

        pass

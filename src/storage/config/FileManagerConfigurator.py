"""
Module used for factory method existent in FileManagerConfigurator.
Module contains the factory class that should not be instantiated.
"""

from src.storage.implementations.FolderFilerManager import FolderFileManager
from src.storage.implementations.FtpFileManager import FtpFileManager
from src.storage.implementations.ZipFileManager import ZipFileManager
from src.validations.ArgsValidator import StorageType


class FileManagerConfigurator:
    """
    Class used as factory for file managers based on storage types passed.

    Methods
    -------
    get_managers(conn_strings: tuple[str], storage_types: tuple[StorageType])
        Instantiates the managers based on storage types
    """

    @staticmethod
    def get_managers(conn_strings: tuple[str], storage_types: tuple[StorageType]) -> tuple:
        """
        Instantiates the managers accordingly to storage types

        Parameters
        ----------
        conn_strings : tuple
            The connection strings necessary for each storage type. Must be valid conn_strings,
            usually validated before used here
        storage_types : tuple
            The storage types identified by parsing the conn_strings by Validator.
        """

        file_manager_list = []
        for index, storage_type in enumerate(storage_types):
            if storage_type == StorageType.FOLDER:
                file_manager_list.append(FolderFileManager(conn_strings[index]))
            elif storage_type == StorageType.ZIP:
                file_manager_list.append(ZipFileManager(conn_strings[index]))
            else:
                file_manager_list.append(FtpFileManager(conn_strings[index]))
        return tuple(file_manager_list)

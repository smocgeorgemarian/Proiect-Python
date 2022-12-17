from storage.implementations.FolderFilerManager import FolderFileManager
from storage.implementations.FtpFileManager import FtpFileManager
from storage.implementations.ZipFileManager import ZipFileManager
from validations.ArgsValidator import StorageType


class FileManagerConfigurator:
    @staticmethod
    def get_managers(conn_strings: list[str], storage_types: list[StorageType]) -> tuple:
        file_manager_list = []
        for index, storage_type in enumerate(storage_types):
            if storage_type == StorageType.FOLDER:
                file_manager_list.append(FolderFileManager(conn_strings[index]))
            elif storage_type == StorageType.ZIP:
                file_manager_list.append(ZipFileManager(conn_strings[index]))
            else:
                file_manager_list.append(FtpFileManager(conn_strings[index]))
        return tuple(file_manager_list)

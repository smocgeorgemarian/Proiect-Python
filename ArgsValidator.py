import os.path
import re
import zipfile
from enum import Enum

FTP = "ftp"
ZIP = "zip"


class StorageType(Enum):
    FTP = 1
    ZIP = 2
    FOLDER = 3


class ArgsValidator:
    def __init__(self, argv: list[str]) -> None:
        self.argv = argv

    @staticmethod
    def is_valid_ftp(conn_string: str) -> bool:
        return re.match(r"ftp:(?#my_user)\w+:(?#my_pass)\w+:(?#folder)\w*",
                        conn_string) is not None

    @staticmethod
    def is_valid_zip(path: str) -> bool:
        local_path = path.split('zip:')[1]
        if not zipfile.is_zipfile(local_path):
            return False

    @staticmethod
    def is_valid_folder(path: str) -> bool:
        return os.path.isdir(path)

    def validate(self) -> tuple[StorageType]:
        if len(self.argv) != 2:
            raise Exception("Script must receive 2 args")

        location_types = []
        for arg in self.argv:
            if arg.startswith(FTP):
                if not self.is_valid_ftp(arg):
                    raise Exception("Invalid FTP location format")
                location_types.append(StorageType.FTP)

            elif arg.startswith(ZIP):
                if not self.is_valid_zip(arg):
                    raise Exception("Invalid local zip file path")
                location_types.append(StorageType.ZIP)

            else:
                if not self.is_valid_folder(arg):
                    raise Exception("Invalid local folder path")
                location_types.append(StorageType.FOLDER)

        return tuple(location_types)

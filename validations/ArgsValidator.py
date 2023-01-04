import os.path
import re
import zipfile
from enum import Enum

from validations.exceptions.ValidationException import ValidationException

FTP = "ftp"
ZIP = "zip"


class StorageType(Enum):
    """
    Class used as enum representing the type of storage
    """

    FTP = 1
    ZIP = 2
    FOLDER = 3


class ArgsValidator:
    """
    Class used for validating

    Validates that the arguments match the regex/represent valid paths in
    the system depending on the platform and storage type

    Attributes
    ----------
    argv : list
        Arguments representing the locations to be synced
    Returns
    -------
    tuple
        Contains the matching storage type for each input argument
    """
    def __init__(self, argv: list[str]) -> None:
        """
        Parameters
        ----------
        argv : list
            Arguments representing the locations to be synced
        """
        self.argv = argv

    def validate(self) -> tuple[StorageType]:
        """
        Maps the arguments to the matching storage type held in ~validations.ArgsValidator.StorageType.

        Returns
        ----------
        location_types : tuple
            Contains the matching StorageType object for every argv provided
        Raises
        ------
        ValidationException
            Class was instantiated with either wrong args or wrong number of args.
        """
        if len(self.argv) != 2:
            raise ValidationException(message="Script must receive 2 args")

        location_types = []
        for arg in self.argv:
            if arg.startswith(FTP):
                if not self.is_valid_ftp(arg):
                    raise ValidationException(location_type="FTP")
                location_types.append(StorageType.FTP)

            elif arg.startswith(ZIP):
                if not self.is_valid_zip(arg):
                    raise ValidationException(location_type="ZIP")
                location_types.append(StorageType.ZIP)

            else:
                if not self.is_valid_folder(arg):
                    raise ValidationException(location_type="LOCAL FOLDER")
                location_types.append(StorageType.FOLDER)
        return tuple(location_types)

    @staticmethod
    def is_valid_ftp(conn_string: str) -> bool:
        """
        Checks whether the connection string is ftp matches regex.

        Parameters
        ----------
        conn_string : str
            Connection string provided for usage of ftp, having a specific format
            consisting of: ftp:my_user:my_pass@URL[/folder].
        Returns
        ----------
        bool
            Regex matches conn_string or not
        """
        return re.match(r"ftp:(?#my_user).+:(?#my_pass).+@(?#URL)(/(?#folder)\w*)?", conn_string) is not None

    @staticmethod
    def is_valid_zip(path: str) -> bool:
        """
        Checks whether the path is a valid .zip file.

        Parameters
        ----------
        path : str
            Path to zip file
        Returns
        ----------
        bool
            Path is a valid .zip file
        """
        local_path = path.split('zip:')[1]
        return zipfile.is_zipfile(local_path)

    @staticmethod
    def is_valid_folder(path: str) -> bool:
        """
        Checks whether the path is a folder.

        Parameters
        ----------
        path : str
            Path to folder
        Returns
        ----------
        bool
            Path is a folder
        """
        return os.path.isdir(path)

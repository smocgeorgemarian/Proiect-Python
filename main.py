import logging
import os.path
import sys
import zipfile

from algorithm.Algorithm import InitAlgorithm
from storage.config.FileManagerConfigurator import FileManagerConfigurator
from storage.implementations.FolderFilerManager import FolderFileManager
from storage.implementations.FtpFileManager import FtpFileManager
from validations.ArgsValidator import ArgsValidator

TEST_FILE = os.path.join(".", "resources", "file.zip")
FOLDER_PATH = "H:\\ftp"


def mock_setup():
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    tmp_zip = zipfile.ZipFile(TEST_FILE, 'w')
    tmp_zip.close()

    # if not os.path.exists(os.path.join(FOLDER_PATH, "to_be_deleted")):
    #     os.mkdir(os.path.join(FOLDER_PATH, "to_be_deleted"))
    #
    # for mock_files in ["a", "b.txt", "c"]:
    #     with open(os.path.join(FOLDER_PATH, mock_files), "w") as fd:
    #         fd.write(mock_files)
    #     with open(os.path.join(FOLDER_PATH, "tests", mock_files), "w") as fd:
    #         fd.write(mock_files)
    #     with open(os.path.join(FOLDER_PATH, "to_be_deleted", mock_files), "w") as fd:
    #         fd.write(mock_files)


def main():
    # mock_setup()

    # logging.basicConfig(encoding='utf-8', level=logging.INFO)
    # argv = sys.argv[1:]
    #
    # validator = ArgsValidator(argv=argv)
    # storage_types = validator.validate()
    # managers = FileManagerConfigurator.get_managers(argv, storage_types)
    #
    # algorithm = InitAlgorithm(managers)
    # algorithm.run()


if __name__ == "__main__":
    main()


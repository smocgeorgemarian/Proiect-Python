import os.path
import zipfile

from algorithm.init_algorithm import InitAlgorithm
from storage.implementations.FolderFilerManager import FolderFileManager
from storage.implementations.FtpFileManager import FtpFileManager
from storage.implementations.ZipFileManager import ZipFileManager

TEST_FILE = os.path.join(".", "resources", "file.zip")


def mock_setup():
    # if os.path.exists(TEST_FILE):
    #     os.remove(TEST_FILE)
    # zip = zipfile.ZipFile(TEST_FILE, 'w')
    # zip.close()
    pass

def main():
    mock_setup()
    first_manager = FtpFileManager(conn_string="ftp:George Smoc:pass@localhost")
    second_manager = FolderFileManager(conn_string="H:\\Anul 3\\local")
    algorithm = InitAlgorithm(first_manager=first_manager,
                              second_manager=second_manager)
    algorithm.run()


if __name__ == "__main__":
    main()

import logging
import os.path
import zipfile

from algorithm.Algorithm import InitAlgorithm
from storage.implementations.FolderFilerManager import FolderFileManager
from storage.implementations.FtpFileManager import FtpFileManager
from storage.implementations.ZipFileManager import ZipFileManager

TEST_FILE = os.path.join(".", "resources", "file.zip")


def mock_setup():
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    tmp_zip = zipfile.ZipFile(TEST_FILE, 'w')
    tmp_zip.close()
    pass


def main1():
    mock_setup()
    first_manager = FtpFileManager(conn_string="ftp:George Smoc:pass@localhost")
    second_manager = FolderFileManager(conn_string="H:\\Anul 3\\local")
    algorithm = InitAlgorithm(first_manager=first_manager,
                              second_manager=second_manager)
    algorithm.run()
    algorithm.keep_syncronized()


def main():
    logging.basicConfig(encoding='utf-8', level=logging.INFO)
    mock_setup()
    first_manager = FolderFileManager(conn_string="H:\\Anul 3\\local")
    second_manager = ZipFileManager(conn_string=TEST_FILE)
    algorithm = InitAlgorithm(first_manager=first_manager,
                              second_manager=second_manager)
    algorithm.run()
    algorithm.keep_syncronized()


if __name__ == "__main__":
    main()

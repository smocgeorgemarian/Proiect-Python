import unittest

from algorithm.init_algorithm import InitAlgorithm
from storage.implementations.FolderFilerManager import FolderFileManager
from storage.implementations.FtpFileManager import FtpFileManager
from storage.implementations.ZipFileManager import ZipFileManager

ZIP_CONN_STRING = "H:\\Anul 3\\Proiect-Python\\file.zip"

class MyTestCase(unittest.TestCase):
    def test_connection(self):
        first_manager = FtpFileManager(conn_string="ftp:George Smoc:pass@localhost")
        # second_manager = FolderFileManager(conn_string=os.path.join(".", ".."))
        # init_alg = InitAlgorithm(first_manager=first_manager, second_manager=second_manager)
        # init_alg.run()

    def test_create_dir(self):
        first_manager = FtpFileManager(conn_string="ftp:George Smoc:pass@localhost")
        first_manager.setup()
        first_manager.dive_into_dir("first_folder")
        first_manager.create_dir("georges")

    def test_zip_folder_sync(self):
        first_manager = ZipFileManager(conn_string="H:\\Anul 3\\Proiect-Python\\tests.zip")
        second_manager = FolderFileManager(conn_string="H:\\Anul 3\\local")
        algorithm = InitAlgorithm(first_manager=first_manager,
                                  second_manager=second_manager)
        algorithm.run()

    def test_ftp_folder_sync(self):
        first_manager = ZipFileManager(conn_string=ZIP_CONN_STRING)
        second_manager = FtpFileManager(conn_string="ftp:George Smoc:pass@localhost")
        algorithm = InitAlgorithm(first_manager=first_manager,
                                  second_manager=second_manager)
        algorithm.run()
        algorithm.keep_syncronized()


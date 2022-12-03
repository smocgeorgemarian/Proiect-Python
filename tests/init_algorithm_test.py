import unittest

from storage.FtpFileManager import FtpFileManager


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

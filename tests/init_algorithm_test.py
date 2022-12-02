import os
import unittest

from algorithm.init_algorithm import InitAlgorithm
from storage.FolderFilerManager import FolderFileManager
from storage.FtpFileManager import FtpFileManager
from storage.ZipFileManager import ZipFileManager


class MyTestCase(unittest.TestCase):
    def test_connection(self):
        first_manager = FtpFileManager(conn_string="ftp:George Smoc:pass@localhost")
        second_manager = FolderFileManager(conn_string=os.path.join(".", ".."))
        init_alg = InitAlgorithm(first_manager=first_manager, second_manager=second_manager)
        init_alg.run()


import os.path
import unittest

from src.storage import FolderFileManager
from src.storage.implementations.FtpFileManager import FtpFileManager
from src.storage.implementations.ZipFileManager import ZipFileManager


class MyTestCase(unittest.TestCase):
    def test_overwrite_zip(self):
        manager = ZipFileManager(conn_string="H:\\Anul 3\\Proiect-Python\\NewZip.zip")
        manager.setup()
        fd = manager.open("ftp_first_file", mode='w')
        fd.write(b'the new content')
        fd.close()

    def test_overwrite_ftp(self):
        manager = FtpFileManager(conn_string="ftp:George Smoc:pass@localhost")
        manager.setup()
        with open(os.path.join("", "resources", "file.tmp"), mode='rb') as fd:
            manager.save_file(path_data="name1", fd_source=fd)

    def test_overwrite_local(self):
        manager = FolderFileManager(conn_string="H:\\Anul 3\\local")
        manager.setup()
        with open(os.path.join("", "resources", "file.tmp"), mode='rb') as fd:
            manager.save_file(path_data="name1", fd_source=fd)

    def test_overwrite_ftp_to_local(self):
        first_manager = FtpFileManager(conn_string="ftp:George Smoc:pass@localhost")
        first_manager.setup()

        second_manager = FolderFileManager(conn_string="H:\\Anul 3\\local")
        second_manager.setup()

        fd_dest = second_manager.open(filename="name1", mode="w")
        first_manager.retrieve_file(path_data="name1", fd_dest=fd_dest)
        second_manager.close(fd_dest)


if __name__ == '__main__':
    unittest.main()

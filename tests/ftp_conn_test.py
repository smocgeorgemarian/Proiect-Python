import unittest

from src.storage.implementations.FtpFileManager import FtpFileManager


class MyTestCase(unittest.TestCase):
    def test_connection(self):
        manager = FtpFileManager(conn_string="ftp:George Smoc:pass@localhost")
        manager.setup()
        print(manager.get_all_files_metadata())

    def test_connection_bad_credentials(self):
        manager = FtpFileManager(conn_string="ftp:admin:pass@localhost")
        self.assertRaises(Exception, manager.setup)

    def test_update_modification_time(self):
        manager = FtpFileManager(conn_string="ftp:George Smoc:pass@localhost")
        manager.setup()
        data_before = manager.get_files_metadata()["Node.java"]
        data_after = manager.get_files_metadata()["Node.java"]
        a = 1

    def test_mlds_command(self):
        manager = FtpFileManager(conn_string="ftp:George Smoc:pass@localhost")
        manager.setup()
        ls = []
        print(manager.ftp.sendcmd('MDTM a'))

if __name__ == '__main__':
    unittest.main()

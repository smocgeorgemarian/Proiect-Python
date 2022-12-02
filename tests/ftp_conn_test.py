import unittest

from storage.FtpFileManager import FtpFileManager


class MyTestCase(unittest.TestCase):
    def test_connection(self):
        manager = FtpFileManager(conn_string="ftp:George Smoc:pass@localhost")
        manager.setup()
        print(manager.get_all_files_metadata())

    def test_connection_bad_credentials(self):
        manager = FtpFileManager(conn_string="ftp:admin:pass@localhost")
        self.assertRaises(Exception, manager.setup)


if __name__ == '__main__':
    unittest.main()

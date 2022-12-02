import unittest

from storage.FtpFileManager import FtpFileManager


class MyTestCase(unittest.TestCase):
    def test_connection(self):
        manager = FtpFileManager(conn_string="ftp:dlpuser:rNrKYTX9g7z3RgJRmxWuGHbeu@ftp.dlptest.com/")
        manager.setup()

if __name__ == '__main__':
    unittest.main()

import unittest
import zipfile

from storage.ZipFileManager import ZipFileManager

CONN_STRING = "./../tests.zip"


class MyTestCase(unittest.TestCase):
    def test_connection_bad_credentials(self):
        manager = ZipFileManager(conn_string="./../Proiect-Python.zip")
        manager.setup()
        fd = manager.open("ArgsValidator.py", )
        print(manager.get_next_chunk(fd))
        manager.close(fd)

    def test_get_dirs(self):
        manager = ZipFileManager(conn_string="./../Proiect-Python.zip")
        manager.setup()
        print(manager.get_dirs())

    def test_get_dirs_after_dive_in_dir(self):
        manager = ZipFileManager(conn_string="./../Proiect-Python.zip")
        manager.setup()
        print(manager.get_files_metadata())

    def test_open_zip_twice_write_2_files(self):
        path = './../NewZip.zip'
        for filename in ['name1', 'name2']:
            with zipfile.ZipFile(path, mode='a') as zip_fd:
                with zip_fd.open(filename, mode='w') as fd:
                    fd.write(b'hehe')

    def test_format_infolist(self):
        manager = ZipFileManager(conn_string=CONN_STRING)
        manager.setup()
        manager.create_dir("dir")
        # manager.refresh()

if __name__ == '__main__':
    unittest.main()
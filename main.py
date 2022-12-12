import os.path
import zipfile

from algorithm.init_algorithm import InitAlgorithm
from storage.FtpFileManager import FtpFileManager
from storage.ZipFileManager import ZipFileManager

TEST_FILE = "file.zip"

ZIP_CONN_STRING = "H:\\Anul 3\\Proiect-Python\\file.zip"

def main():
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)

    zipfile.ZipFile(TEST_FILE, 'w')
    first_manager = ZipFileManager(conn_string=ZIP_CONN_STRING)
    second_manager = FtpFileManager(conn_string="ftp:George Smoc:pass@localhost")
    algorithm = InitAlgorithm(first_manager=first_manager,
                              second_manager=second_manager)
    algorithm.run()
    # algorithm.keep_syncronized()

if __name__ == "__main__":
    main()


if __name__ == '__main__':
    main()


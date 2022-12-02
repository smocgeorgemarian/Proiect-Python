import os.path
import zipfile
from datetime import datetime

from storage.FileManager import FileManager


class ZipFileManager(FileManager):
    def __init__(self, conn_string: str):
        super().__init__(conn_string)
        self.path = conn_string
        self.zip = None

    def setup(self):
        self.zip = zipfile.ZipFile(self.path)

    def write_to_file_buffered(self, filename):
        with zipfile.ZipFile(self.path, mode='w') as zip:
            with zip.open(filename, mode='w') as fd:
                fd.write(b"testing")


    @staticmethod
    def to_mili_from_epoch(date_time):
        return (datetime(date_time[0], month=date_time[1], day=date_time[2], hour=date_time[3], minute=date_time[4],
                         second=date_time[5]) - datetime(1970, month=1, day=1)).total_seconds()

    def get_all_files_metadata(self):
        return [(file_meta.filename, self.to_mili_from_epoch(file_meta.date_time)) for file_meta in self.zip.infolist()]


if __name__ == "__main__":
    manager = ZipFileManager(conn_string=os.path.join("..", "Proiect.zip"))
    manager.setup()
    metadata = manager.get_all_files_metadata()
    for element in metadata:
        print(element)
    manager.write_to_file_buffered(filename="./aici/dincolo/test.txt")

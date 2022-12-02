import os

from storage.FileManager import FileManager


class FolderFileManager(FileManager):
    def __init__(self, conn_string: str):
        super().__init__(conn_string)
        self.path = conn_string

    def get_all_files_metadata(self):
        return [(os.path.join(root, file), os.stat(os.path.join(root, file)).st_mtime)
                for root, dirs, files in os.walk(self.path)
                for file in files]

    def setup(self):
        pass


if __name__ == "__main__":
    manager = FolderFileManager(conn_string=os.path.join(".."))
    manager.setup()
    metadata = manager.get_all_files_metadata()
    for element in metadata:
        print(element)

import os

from storage.FileManager import FileManager


class FolderFileManager(FileManager):
    def __init__(self, conn_string: str):
        super().__init__(conn_string)
        self.path = conn_string
        self.metadata = dict()
        self.current_dirs = []

    def __get_all_files_metadata__(self):
        full_root_path = os.path.join(self.path, *self.current_dirs)
        self.metadata = dict()
        for maybe_file in os.listdir(full_root_path):
            actual_path = os.path.join(full_root_path, maybe_file)
            if os.path.isfile(actual_path):
                self.metadata[maybe_file] = os.stat(actual_path).st_mtime

    def get_all_files_metadata(self):
        self.__get_all_files_metadata__()
        return self.metadata

    def get_all_dirs(self):
        full_root_path = os.path.join(self.path, *self.current_dirs)
        return  [maybe_dir for maybe_dir in os.listdir(full_root_path)
                if os.path.isdir(os.path.join(full_root_path, maybe_dir))]

    def dive_into_dir(self, child_dir: str):
        if os.path.exists(os.path.join(self.path, *self.current_dirs, child_dir)):
            self.current_dirs.append(child_dir)

    def leave_current_dir(self):
        self.current_dirs.pop()

    def setup(self):
        pass


if __name__ == "__main__":
    manager = FolderFileManager(conn_string=os.path.join(".."))
    manager.setup()
    metadata = manager.get_all_files_metadata()
    for element in metadata:
        print(element)

from abc import abstractmethod


class FileManager:
    def __init__(self, conn_string: str):
        self.conn_string = conn_string

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def retrieve_file(self, filename, fd_dest):
        pass

    @abstractmethod
    def save_file(self, filename, fd_source):
        pass

    @abstractmethod
    def dive_into_dir(self, directory):
        pass

    @abstractmethod
    def leave_dir(self, directory):
        pass

    @abstractmethod
    def get_files_metadata(self):
        pass

    @abstractmethod
    def get_dirs(self):
        pass

    @abstractmethod
    def create_dir(self):
        pass

    @abstractmethod
    def remove_dir(self):
        pass

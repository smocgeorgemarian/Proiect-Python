from abc import abstractmethod


class FileManager:
    def __init__(self, conn_string: str):
        self.conn_string = conn_string

    @abstractmethod
    def get_all_files_metadata(self):
        pass

    @abstractmethod
    def setup(self):
        pass

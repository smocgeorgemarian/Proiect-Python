from storage.FileManager import FileManager


class InitAlgorithm:
    def __init__(self, first_manager: FileManager, second_manager: FileManager):
        self.first_manager, self.second_manager = first_manager, second_manager

    def run(self):
        self.first_manager.setup()
        self.second_manager.setup()

        first_meta = self.first_manager.get_all_files_metadata()
        second_meta = self.second_manager.get_all_files_metadata()
        print(first_meta)
        print(second_meta)


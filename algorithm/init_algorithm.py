from storage.FileManager import FileManager


class InitAlgorithm:
    def __init__(self, first_manager: FileManager, second_manager: FileManager):
        self.first_manager, self.second_manager = first_manager, second_manager
        self.temp_file = 'file.tmp'

    def syncronize_locations(self, first_meta, first_manager,
                             second_meta, second_manager):
        for file in first_meta:
            if file not in second_meta:
                with open(self.temp_file, 'wb') as fd:
                    first_manager.retrieve_file(file, fd)
                with open(self.temp_file, 'rb') as fd:
                    second_manager.save_file(file, fd)
            elif first_meta[file] > second_meta[file]:
                with open(self.temp_file, 'wb') as fd:
                    first_manager.retrieve_file(file, fd)
                with open(self.temp_file, 'rb') as fd:
                    second_manager.save_file(file, fd)

    def __run__(self):
        self.first_manager.setup()
        self.second_manager.setup()

        first_meta = self.first_manager.get_all_files_metadata()
        second_meta = self.second_manager.get_all_files_metadata()

        self.syncronize_locations(first_meta, self.first_manager,
                                  second_meta, self.second_manager)
        self.syncronize_locations(second_meta, self.second_manager,
                                  first_meta, self.first_manager)

        first_dirs = self.first_manager.get_all_dirs()
        second_dirs = self.first_manager.get_all_dirs()

        all_dirs = set(first_dirs) | set(second_dirs)
        for directory in all_dirs:
            self.first_manager.create_dir(directory)
            self.second_manager.create_dir(directory)


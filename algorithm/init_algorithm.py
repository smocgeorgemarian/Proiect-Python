from storage.FileManager import FileManager


class InitAlgorithm:
    def __init__(self, first_manager: FileManager, second_manager: FileManager):
        self.first_manager, self.second_manager = first_manager, second_manager

    def syncronize_locations(self, first_meta, first_manager,
                             second_meta, second_manager):
        for file in first_meta:
            if file not in second_meta:
                second_manager.save_file(file, )


    def __run__(self):
        first_meta = self.first_manager.get_all_files_metadata()
        second_meta = self.second_manager.get_all_files_metadata()

        self.syncronize_locations(first_meta, self.first_manager,
                                  second_meta, self.second_manager)
        self.syncronize_locations(second_meta, self.second_manager,
                                  first_meta, self.first_manager)

        first_dirs = set(self.first_manager.get_all_dirs())
        second_dirs = set(self.first_manager.get_all_dirs())

        all_dirs = set(first_dirs) | set(second_dirs)
        first_to_be_added = all_dirs - second_dirs
        second_to_be_added = all_dirs - first_dirs
        for directory in first_to_be_added:
            self.first_manager.create_dir(directory)
        for directory in second_to_be_added:
            self.second_manager.create_dir(directory)

        for directory in all_dirs:
            self.first_manager.dive_into_dir(directory)
            self.second_manager.dive_into_dir(directory)
            self.__run__()
            self.first_manager.leave_dir()
            self.second_manager.leave_dir()

    def run(self):
        self.first_manager.setup()
        self.second_manager.setup()
        self.__run__()
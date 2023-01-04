class PathData:
    def __init__(self, path_data: tuple, is_file: bool = True, modif_data: float = None) -> None:
        self.path_data = path_data
        self.is_file = is_file
        self.modif_data = modif_data

    def __hash__(self):
        return hash((self.path_data, self.is_file))

    def __str__(self):
        return f"{self.path_data}, {self.is_file}"

    def __repr__(self):
        return f"{self.path_data}, {self.is_file}"

    def __eq__(self, other):
        if not isinstance(other, PathData):
            return False
        return self.path_data == other.path_data and self.is_file == other.is_file

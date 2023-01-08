"""
Module used for internal representations of path in
common format. Functions for hash and equality are
override for future extension of PathData class that
should not influence the values mentioned above.
"""


class PathData:
    """
    Class used for applying continuously syncing between 2 locations

    Attributes
    ----------
    path_data : tuple
        Path of the file/folder split, so it can be kept in a common format for all type of
        locations (not including separator)
    is_file : bool
        Path corresponds to a file or not (default True)
    modif_data : float
        Time in seconds from epoch representing modification date of the file
        (default None for folders)
    """

    def __init__(self, path_data: tuple, is_file: bool = True, modif_data: float = None) -> None:
        """
        Parameters
        ----------
        path_data : tuple
            Path of the file/folder split, so it can be kept in a common format for all type of
            locations (not including separator)
        is_file : bool
            Path corresponds to a file or not (default True)
        modif_data : float
            Time in seconds from epoch representing modification date of the file
            (default None for folders). Currently, not used.
        """

        self.path_data = path_data
        self.is_file = is_file
        self.modif_data = modif_data

    def __hash__(self):
        """
        Hash of the path contains strictly the relative path and the is_file flag.

        Created in this way for future extensions of the class so the new attributes
        will not interfere with the hash value.
        """
        return hash((self.path_data, self.is_file))

    def __str__(self):
        """Visual representation of the path, useful for debugging"""
        return f"{self.path_data}, {self.is_file}"

    def __repr__(self):
        """Visual representation of the path, useful for debugging"""
        return f"{self.path_data}, {self.is_file}"

    def __eq__(self, other):
        """
        Checks the equality of the current object with other object

        Parameters
        ----------
        other
            Any other object with which the current object will be compared
        Returns
        ----------
            True if objects are equal, False otherwise
        """
        if not isinstance(other, PathData):
            return False
        return self.path_data == other.path_data and self.is_file == other.is_file

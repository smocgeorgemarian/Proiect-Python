import unittest

from storage.model.PathData import PathData


class PathDataTest(unittest.TestCase):
    def test_hash(self):
        # arrange
        storage = set()
        path_data = PathData(path_data=("test", "test"), modif_data=123)
        updated_path_data = PathData(path_data=("test", "test"), modif_data=1234)
        # act
        storage.add(path_data)
        storage.add(updated_path_data)
        # assert
        self.assertEqual(1, len(storage))  # add assertion here


if __name__ == '__main__':
    unittest.main()

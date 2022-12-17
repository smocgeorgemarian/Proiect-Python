import unittest
from pathlib import PurePath


class MyTestCase(unittest.TestCase):
    def test_overwrite_zip(self):
        self.assertEqual("georges", PurePath("/home/georges").name)


if __name__ == '__main__':
    unittest.main()

import logging
import os.path
import sys
import zipfile

from algorithm.Algorithm import InitAlgorithm
from storage.config.FileManagerConfigurator import FileManagerConfigurator
from validations.ArgsValidator import ArgsValidator

TEST_FILE = os.path.join(".", "resources", "file.zip")
FOLDER_PATH = "H:\\ftp"


def mock_setup():
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    tmp_zip = zipfile.ZipFile(TEST_FILE, 'w')
    info = zipfile.ZipInfo("tests/")
    tmp_zip.writestr(info, '')

    for content in ['a', 'b', 'c']:
        with tmp_zip.open(content, 'w') as fd:
            fd.write(str.encode(content))
    tmp_zip.close()

def main():
    mock_setup()

    logging.basicConfig(encoding='utf-8', level=logging.INFO)
    argv = sys.argv[1:]

    validator = ArgsValidator(argv=argv)
    storage_types = validator.validate()
    managers = FileManagerConfigurator.get_managers(argv, storage_types)

    algorithm = InitAlgorithm(managers)
    algorithm.run()


if __name__ == "__main__":
    main()

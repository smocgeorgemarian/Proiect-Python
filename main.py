import sys

import logging
from algorithm.Algorithm import Algorithm
from storage.config.FileManagerConfigurator import FileManagerConfigurator
from validations.ArgsValidator import ArgsValidator


def main():
    logging.basicConfig(encoding='utf-8', level=logging.INFO)
    argv = sys.argv[1:]

    validator = ArgsValidator(argv=argv)
    storage_types = validator.validate()
    managers = FileManagerConfigurator.get_managers(argv, storage_types)

    algorithm = Algorithm(managers)
    algorithm.run()


if __name__ == "__main__":
    main()

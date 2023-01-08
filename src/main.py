"""
Module used as entry point in command-line application. Contains the
main function that sets up the environment based on arguments and
their mappings as internal objects. Throws error in case of
invalid args.
"""
import sys

import logging
from src.algorithm.Algorithm import Algorithm
from src.storage.config.FileManagerConfigurator import FileManagerConfigurator
from src.validations.ArgsValidator import ArgsValidator


def main():
    """
    Obtains sys args and runs sync algorithm on the corresponding file managers.

    Raises
    ------
    ValidationException
        If arguments provided were not respecting enstablished format
    """
    logging.basicConfig(encoding='utf-8', level=logging.INFO)
    argv = sys.argv[1:]

    validator = ArgsValidator(argv=argv)
    storage_types = validator.validate()
    managers = FileManagerConfigurator.get_managers(argv, storage_types)

    algorithm = Algorithm(managers)
    algorithm.run()


if __name__ == "__main__":
    main()

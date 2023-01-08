class ValidationException(Exception):
    """Exception raised for errors in validation of application args."""

    def __init__(self, message: str = None, location_type: str = None) -> None:

        if message is not None:
            super().__init__(message)
        elif location_type is not None:
            super().__init__(f"Could not validate location of type {location_type}")
        else:
            super().__init__(f"Could not validate current location type")

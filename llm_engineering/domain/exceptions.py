class LLMTwinException(Exception):
    """
    Base exception class for LLMTwin related errors.

    This class serves as the parent exception class for all custom exceptions
    within the LLMTwin system.
    """

    pass


class ImproperlyConfiguredException(LLMTwinException):
    """
    Exception raised when configuration is incorrect or missing.

    This exception is raised when the system encounters improper or missing
    configuration settings that are required for proper operation.
    """

    pass

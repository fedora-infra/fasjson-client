class BaseError(Exception):
    """
    Base exception class that is in inherited from all other exceptions.
    """

    def __init__(self, message, code, data=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data

    def __repr__(self):
        """
        String representation of the class for debugging purposes,
        returned when using the repr function.
        """
        return (
            f"<{self.__class__.__name__} code={self.code} "
            f"message={self.message} data={self.data}>"
        )

    def __str__(self):
        """
        value returned by the str() function.
        """
        return self.message


class ClientError(BaseError):
    """
    Client exception whcih is raised in case of openapi spec and client setup issues.
    """

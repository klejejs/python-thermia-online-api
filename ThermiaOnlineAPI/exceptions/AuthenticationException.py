class AuthenticationException(Exception):
    """
    Exception raised when the authentication fails.
    """

    def __init__(self, message, status=None):

        super().__init__(message)

        self.status = status

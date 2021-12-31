class NetworkException(Exception):
    """
    Exception raised when the network fails.
    """

    def __init__(self, message, status=None):

        super().__init__(message)

        self.status = status

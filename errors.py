class CustomError(Exception):

    def __init__(self, message, error_code=None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
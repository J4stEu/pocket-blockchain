class BcSystemError(Exception):
    def __init__(self, error_type, error_message, message="blockchain system error."):
        self.error_type = error_type
        self.error_message = error_message
        self.message = message
        super().__init__(self.message)
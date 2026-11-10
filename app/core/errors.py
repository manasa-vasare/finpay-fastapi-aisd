class AppError(Exception):
    """Business error raised by the service layer, converted to an HTTP response in main.py"""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

class GSpreadException(Exception):
    pass

class AuthenticationError(GSpreadException):
    pass

class SpreadsheetNotFound(GSpreadException):
    pass

class NoValidUrlKeyFound(GSpreadException):
    pass

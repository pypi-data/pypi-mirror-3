class HttpException(Exception):
    """ Exception for Http Errors"""
    def __init__(self, message, status=500):
        self.status = status
        super(HttpException, self).__init__(message)

class HttpException(Exception):
    """ Exception for Http Errors"""
    def __init__(self, message=None, status=500):
        self.status = status
        super(HttpException, self).__init__(message)

def bubble_message(old_exception, new_exception):
    if not getattr(new_exception, "message", False):
        new_exception.message = getattr(old_exception, "message", None)
    return new_exception

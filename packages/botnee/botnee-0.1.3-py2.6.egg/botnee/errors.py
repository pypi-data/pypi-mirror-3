"""
Custom error handlers
"""
import warnings

#from botnee import debug

class BotneeException(Exception):
    def __init__(self, value, logger=None):
        self.parameter = value
        if logger and value:
            logger.error(value)
    
    def __str__(self):
        return repr(self.parameter)


class BotneeWarning(object):
    def __init__(self, message, logger=None):
        if message:
            warnings.warn(message)
            if logger:
                logger.warn(message)

class EngineError(BotneeException):
    """Custom error handler for engine class"""
    pass

class EngineWarning(BotneeWarning):
    """Custom warning handler for engine class"""
    pass

class DocManagerError(BotneeException):
    """Custom error handler for document store"""
    pass

class DocStoreError(BotneeException):
    """Custom error handler for document store"""
    pass

class DocStoreWarning(BotneeWarning):
    """Custom warning handler for the document store"""
    pass

class ProcessError(BotneeException):
    """Custom error handler for the process module"""
    pass

class ProcessWarning(BotneeWarning):
    """Custom warning handler for the process module"""
    pass

class StandardDocumentError(BotneeException):
    """Custom error handler for standard document io"""
    pass

class GetRelatedError(BotneeException):
    """Custom error handler for GetRelated"""
    pass

class GetRelatedWarning(BotneeWarning):
    """Custom warning handler for GetRelated"""
    pass

class FiltersWarning(BotneeWarning):
    """Custom warning handler for Filters"""
    pass

class RssWriterWarnging(BotneeWarning):
    """Custom warning handler for rss_writer"""
    pass



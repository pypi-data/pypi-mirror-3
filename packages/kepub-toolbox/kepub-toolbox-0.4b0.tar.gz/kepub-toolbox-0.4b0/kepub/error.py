"""Module for exceptions raised by this package"""
__author__ = 'Stefano Quaranta'
__author_email__ = 'steppo40@gmail.com'
__owner__ = 'Ecomind Srl'
from kepub import get_version
__version__ = get_version()


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class TransformationError(Error):
    """Exception raised for error during a transformation
    
    Attributes:
        msg  -- explanation of the error
    
    """
    
    def __init__(self, msg):
        self.msg = msg
        
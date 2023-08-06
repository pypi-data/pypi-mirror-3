class FBException(Exception):
    """
    Generic exception as a convenience to the client, if they don't care
    to handle different exception types differently.
    """
    pass

class FBHTTPException(FBException):
    """
    This exception is raised for HTTP errors encountered, i.e. a non-200 HTTP
    status codes.
    """
    pass

class FBJSONException(FBException):
    """
    This exception is raised when the JSON response cannot be deserialized
    properly.
    """

class FBConnectionException(FBException):
    """
    This exception is raised for errors encountered at the connection level,
    like timeout errors, SSL errors, etc.
    """
    pass
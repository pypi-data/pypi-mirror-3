class SocialtextException(Exception):
    """
    The base exception class for all exceptions this library raises.
    """
    def __init__(self, code, message=None):
        self.code = code
        self.message = message
        
    def __str__(self):
        return "%s (HTTP %s)" % (self.message, self.code)


class BadRequest(SocialtextException):
    """
    HTTP 400 - Bad request: you sent some malformed data.
    """
    http_status = 400
    message = "Bad request"


class Unauthorized(SocialtextException):
    """
    HTTP 401 - Unauthorized: bad credentials.
    """
    http_status = 401
    message = "Unauthorized"


class Forbidden(SocialtextException):
    """
    HTTP 403 - Forbidden: your credentials don't give you
    access to this resource.
    """
    http_status = 403
    message = "Forbidden"


class NotFound(SocialtextException):
    """
    HTTP 404 - Not found
    """
    http_status = 404
    message = "Not found"


class Conflict(SocialtextException):
    """
    HTTP 409 - Conflict
    """
    http_status = 409
    message = "Conflict"


class RequestEntityTooLarge(SocialtextException):
    """
    HTTP 413 - Request entity too large: The data size can not exceed 50MB.
    """
    http_status = 413
    message = "Request entity too large"
    
class ServiceUnavailable(SocialtextException):
    """
    HTTP 503 - Service Unavailable
    """
    http_status = 503
    message = "Service unavailable. The server is unable to handle the request due to "\
              "temporary overload or maintenance."

_code_map = dict((c.http_status, c) for c in [BadRequest, Unauthorized,
    Forbidden, NotFound, Conflict, RequestEntityTooLarge, ServiceUnavailable])


def from_response(response, body):
    """
    Return an instance of a SocialtextException or subclass
    based on an httplib2 response.
    
    Usage::
    
        resp, body = http.request(...)
        if resp.status != 200:
            raise exceptions.from_response(resp, body)
    """
    cls = _code_map.get(response.status_code, SocialtextException)
    if body:
        error = body
        return cls(code=response.status_code, message=body)
    else:
        return cls(code=response.status_code)


def from_urllib2_exception(exc):
    """
    Return an instance of a SocialtextException or subclass
    based on an urllib2 exception.

    Usage::

        try:
            urllib2.urlopen(url)
        except urllib2.HTTPError, exc:
            raise exceptions.from_urllib2_exception(exc)
    """
    cls = _code_map.get(exc.code, SocialtextException)
    msg = None
    if hasattr(exc, 'read'):
        msg = exc.read()
    if msg:
        return cls(code=exc.code, message=msg)
    else:
        return cls(code=exc.code)

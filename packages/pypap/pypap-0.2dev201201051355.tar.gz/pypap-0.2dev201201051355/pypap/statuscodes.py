class Status(object):
    """
    A Status has a 4-digit numerical value called a `code'.

    The first digit represents the class of the code.  There are
    five classes:

         - 1xxx: Success
         - 2xxx: Client Error
         - 3xxx: Server Error
         - 4xxx: Service Failure
         - 5xxx: Mobile Device Abort

    Implementation-specific codes should be in the range x500 -
    x999.
    """

    code = None
    _string_descriptions = {}

    @property
    def description(self):
        return self._code_descriptions.get(self.code)


class Success(Status):

    _code_descriptions = {'1000': "OK",
                          '1001': "Accepted for Processing"}

    def __init__(self, code):
        if not code.startswith("1"):
            raise ValueError, "{0} is not a valid Success code.".format(
                code)
        self.code = code


class ClientError(Status):

    _code_descriptions = {'2000': "Bad Request",
                          '2001': "Forbidden",
                          '2002': "Address Error",
                          '2003': "Address Not Found",
                          '2004': "Push ID Not Found",
                          '2005': "Capabilities Mismatch",
                          '2006': "Required Capabilities Not Supported",
                          '2007': "Duplicate Push ID",
                          '2008': "Cancellation Not Possible"}

    def __init__(self, code):
        if not code.startswith("2"):
            raise ValueError, "{0} is not a valid ClientError code.".format(
                code)
        self.code = code


class ServerError(Status):

    _code_descriptions = {'3000': "Internal Server Error",
                          '3001': "Not Implemented",
                          '3002': "Version Not Supported",
                          '3003': "Not Possible",
                          '3004': "Capability Matching Not Supported",
                          '3005': "Multiple Addresses Not Supported",
                          '3006': "Transformation Failure",
                          '3007': "Specified Delivery Method not Possible",
                          '3008': "Capabilities Not Available",
                          '3009': "Required Network Not Available",
                          '3010': "Required Bearer Not Available",
                          '3011': "Replacement Not Supported"}

    def __init__(self, code):
        if not code.startswith("3"):
            raise ValueError, "{0} is not a valid ServerError code.".format(
                code)
        self.code = code


class ServiceFailure(Status):

    _code_descriptions = {'4000': "Service Failure",
                          '4001': "Service Unavailable"}

    def __init__(self, code):
        if not code.startswith("4"):
            raise ValueError, "{0} is not a valid ServiceFailure code.".format(
                code)
        self.code = code


class MobileDeviceAbort(Status):
    pass


DEFAULT_CLASSES = {'1': Success,
                   '2': ClientError,
                   '3': ServerError,
                   '4': ServiceFailure,
                   '5': MobileDeviceAbort}


def get_status(code, status_classes=DEFAULT_CLASSES):
    """
    Return a suitable instance representing `code'.

    `code': A string representation of the status code.
    """
    cls = status_classes.get(code[0])
    if not cls:
        raise ValueError, "No available Status for handling {0}.".format(
            code)

    return cls(code)

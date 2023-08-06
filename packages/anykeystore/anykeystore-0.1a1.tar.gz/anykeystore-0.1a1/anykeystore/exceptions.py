class ConfigurationError(object):
    """ Raised when configuration fails on a backend."""

    def __init__(self, message):
        self.message = message

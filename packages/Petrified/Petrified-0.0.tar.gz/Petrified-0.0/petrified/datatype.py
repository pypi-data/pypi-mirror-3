from petrified.lib import new_instance


class DataType(object):

    _spec = None

    # set by widget; weakref proxy
    widget = None

    error_message = u'Invalid type'

    def __init__(self, error_message=None):
        self.error_message = error_message or self.error_message

        # Save original instance settings
        self._spec = {
            'error_message': error_message
        }

    def new(self):
        return new_instance(self)

    def to_type(self, value):
        """ converts a raw string to the appropriate type """
        return value

    def to_string(self, value):
        """ converts the "complex" type to a string """
        return value

    def is_empty(self, value):
        return False

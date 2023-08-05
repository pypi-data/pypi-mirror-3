import inspect

from petrified.lib import new_instance


class Validator(object):

    error_message = u''
    error_class = u''

    # weakref proxy to widget instance; set by widget's __init__
    widget = None

    def __init__(self, error_message=u'', error_class=u'', *args, **kwargs):
        self.error_message = error_message or self.error_message
        self.error_class = error_class \
                           or self.error_class \
                           or self.__class__.__name__.lower()

        # Save original instance settings
        self._spec = {
            'error_message': error_message,
            'error_class': error_class
        }
        for kw in kwargs:
            self._spec[kw] = kwargs[kw]

    def new(self):
        return new_instance(self)

    def apply_error(self, error_message=None, error_class=None):
        error_message = error_message or self.error_message
        error_class = error_class or self.error_class
        self.widget.errors.add((self.error_class, self.error_message))

    def validate(self):
        """ returns True if valid, False if... not """
        return True

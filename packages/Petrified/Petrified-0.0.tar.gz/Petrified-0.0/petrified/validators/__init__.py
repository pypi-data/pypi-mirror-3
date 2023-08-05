import re

from petrified.validator import Validator


class Required(Validator):
    error_message = u'This field is required.'

    def validate(self):
        if self.widget.datatype.is_empty(self.widget.value):
            self.apply_error()
            return False
        return True


class RegEx(Validator):
    error_message = u'Incorrect format.'
    regex = None
    mode = None

    def __init__(self, regex, mode=None, *args, **kwargs):
        kwargs['regex'] = regex
        kwargs['mode'] = mode
        Validator.__init__(self, *args, **kwargs)
        self.regex = regex
        self.mode = mode

    def validate(self):
        if self.mode:
            m = re.match(self.regex,
                         self.widget.datatype.to_string(self.widget.value),
                         self.mode)
        else:
            m = re.match(self.regex,
                         self.widget.datatype.to_string(self.widget.value))
        if not m or not m.group(0):
            self.apply_error()
            return False
        return True


class Email(RegEx):
    error_message = u'Please specify a valid email address.'
    regex = '[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}'
    mode = re.I

    def __init__(self, error_message=u'', error_class='', *args, **kwargs):
        RegEx.__init__(self, self.regex, re.I, error_message, error_class,
                       *args, **kwargs)


class SameAs(Validator):
    field = None

    def __init__(self, field, error_message=u'', error_class=u'',
                 *args, **kwargs):
        kwargs['field'] = field
        error_message = error_message or u'Needs to match %s' % field
        Validator.__init__(self, error_message, error_class, *args, **kwargs)
        self.field = field

    def validate(self):
        if self.widget.value != getattr(self.widget.form, self.field).value:
            self.apply_error()
            return False
        return True

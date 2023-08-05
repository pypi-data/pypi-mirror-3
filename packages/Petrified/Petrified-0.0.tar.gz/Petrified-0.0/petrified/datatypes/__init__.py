from petrified.datatype import DataType


class String(DataType):

    def is_empty(self, value):
        if not value:
            return True
        if len(value) == 0:
            return True
        return False

    def to_type(self, value):
        if value == None:
            return ''
        else:
            try:
                return str(value)
            except:
                return ''


class Unicode(DataType):

    def is_empty(self, value):
        if not value:
            return True
        if len(value) == 0:
            return True
        return False

    def to_type(self, value):
        if value == None:
            return u''
        else:
            try:
                return unicode(value)
            except:
                return u''


class Number(DataType):

    def to_type(self, value):
        try:
            value = float(value)
            if value == int(value):
                return int(value)
            return value
        except:
            self.widget.errors.add(('invalid_type', self.error_message))
            return None

    def to_string(self, value):
        return u'%s' % value


class Boolean(DataType):

    def to_type(self, value):
        return value and True or False

    def to_string(self, value):
        return value and 'True' or ''

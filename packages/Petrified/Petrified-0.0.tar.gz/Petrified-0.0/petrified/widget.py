import inspect
import weakref

from petrified.lib import new_instance
from datatypes import String


class Widget(object):

    _order = 0
    _spec = None

    # weakref proxy to form; set automatically by the form
    form = None

    # Will be set automatically by the form
    name = None

    _value = None
    template = 'widget.html'

    def __init__(self, title=None, desc=None, datatype=None, validators=None,
                 render_callback=None, *args, **kwargs):
        # Set global widget order to ensure proper rendering
        self._order = Widget._order
        Widget._order += 1

        validators = validators or []
        datatype = datatype or String

        # Let's save the initial init values...
        self._spec = {}
        for arg in filter(lambda x: x not in ['self'],
                          inspect.getargspec(self.__init__).args):
            self._spec[arg] = locals().get(arg) or kwargs.get(arg)
        for kw in kwargs:
            self._spec[kw] = kwargs[kw]

        self.title = title or u''
        self.desc = desc or u''

        # create instance of type or simply assign
        # TODO: Gotta be a clearer way to determine if it's instantiated
        self.datatype = type(datatype) == type and datatype() or datatype
        ref = weakref.proxy(self)
        self.datatype.widget = ref
        self.validators = validators

        self.errors = set()
        validators = []
        for v in self.validators:
            if inspect.isclass(v):
                v = v()
            v.widget = ref
            validators.append(v)
        self.validators = validators
        self.attrs = {}
        for kw in kwargs:
            if kw == 'value':
                self.value = self.datatype.to_type(kwargs[kw])
            else:
                self.attrs[kw] = kwargs[kw]

        self.render_callback = render_callback

    def new(self):
        return new_instance(self)

    def _set_value(self, value):
        self._value = self.datatype.to_type(value)
    def _get_value(self):
        return self.datatype.to_type(self._value)
    value = property(_get_value, _set_value)

    @property
    def value_repr(self):
        return self.datatype.to_string(self.value)

    def render_label(self):
        if self.form:
            self.form._rendered_widgets.add(self.name)
        if self.render_callback:
            return self.render_callback('widget', self, 'label') or u''
        return u''
    label = property(render_label)

    def render_field(self):
        if self.form:
            self.form._rendered_widgets.add(self.name)
        self.value = self.datatype.to_string(self.value)
        if self.render_callback:
            return self.render_callback('widget', self, 'field') or u''
        self.value = self.datatype.to_type(self.value)
        return ''
    field = property(render_field)

    def __str__(self):
        if self.form:
            self.form._rendered_widgets.add(self.name)
        if self.render_callback:
            return self.render_callback('widget', self) or u''
        return (self.label + self.field) or u''

    def validate(self):
        self.errors = set()
        valid = True
        for v in self.validators:
            if not v.validate():
                valid = False
        return valid

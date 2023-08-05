import weakref

from petrified.widget import Widget
from petrified.lib import new_instance
from petrified.renderers import petrified_jinja2


PROTECTED_PROPERTIES = [
    'validate',
    'render',
    'digest',
    'ingest',
    'form_open',
    'form_close',
    'form_content',
    'form_errors',
    '_widget_names'
]


class Form(object):

    _form = None
    _rendered_widgets = None
    _render_open = True
    _render_content = True
    _render_close = True
    _render_callback = None
    _attrs = {}

    def __init__(self, data={}, render_callback=petrified_jinja2, *args, **kwargs):
        ref = weakref.proxy(self)
        self._rendered_widgets = set()
        self.form_errors = set()

        for wn in self._widget_names:
            widget = getattr(self, wn)
            widget = new_instance(widget)
            setattr(self, wn, widget)
            widget.name = wn
            widget.form = ref
            # A form render_callback is a default for all widgets' render_callback
            if render_callback and not widget.render_callback:
                widget.render_callback = render_callback

        # If there's a dataset that's been given, map values to widgets.
        self.ingest(data)

        self._attrs = { 'method': 'post' }
        for kw in kwargs:
            self._attrs[kw] = kwargs[kw]

        self._render_callback = render_callback

    def ingest(self, data):
        for widget in self:
            if hasattr(data, widget.name):
                widget.value = widget.datatype.to_type(getattr(data, widget.name))
            elif isinstance(data, dict) and widget.name in data:
                widget.value = widget.datatype.to_type(data[widget.name])

    def digest(self, dest):
        if isinstance(dest, dict):
            for widget in self:
                dest[widget.name] = widget.value
        else:
            for widget in self:
                setattr(dest, widget.name, widget.value)

    def validate(self):
        self.form_errors = set()
        valid = True
        for widget in self:
            if not widget.validate():
                valid = False
        return valid

    validates = validate

    def render(self):
        if self._rendered_widgets:
            self._render_open = False
            self._render_close = False
        content = u''
        for widget in self:
            if widget.name not in self._rendered_widgets:
                content += unicode(widget) or u''
        self._rendered_widgets = set()
        return self._render_callback('form', self, content)

    def __str__(self):
        return self.render()

    @property
    def form_open(self):
        render_open          = self._render_open
        render_content       = self._render_content
        render_close         = self._render_close
        self._render_open    = True
        self._render_content = False
        self._render_close   = False
        r = self._render_callback('form', self)
        self._render_open    = render_open
        self._render_content = render_content
        self._render_close   = render_close
        return r

    @property
    def form_content(self):
        render_open          = self._render_open
        render_content       = self._render_content
        render_close         = self._render_close
        self._render_open    = False
        self._render_content = True
        self._render_close   = False
        rendered_widgets     = [rw for rw in self._rendered_widgets]
        content = u''
        for widget in self:
            content += unicode(widget) or u''
        r = self._render_callback('form', self, content)
        self._render_open      = render_open
        self._render_content   = render_content
        self._render_close     = render_close
        self._rendered_widgets = rendered_widgets
        return r

    @property
    def form_close(self):
        render_open          = self._render_open
        render_content       = self._render_content
        render_close         = self._render_close
        self._render_open    = False
        self._render_content = False
        self._render_close   = True
        r = self._render_callback('form', self)
        self._render_open    = render_open
        self._render_content = render_content
        self._render_close   = render_close
        return r

    @property
    def _widget_names(self):
        widgets = []
        for prop in dir(self):
            if prop.startswith('_'):
                continue
            if prop in PROTECTED_PROPERTIES:
                continue
            if hasattr(getattr(self, prop), '_order'):
                widgets.append([prop, getattr(self, prop)._order])
        widgets = sorted(widgets, key=lambda i: i[1])
        return [w[0] for w in widgets]

    def __iter__(self):
        for wn in self._widget_names:
            yield getattr(self, wn)

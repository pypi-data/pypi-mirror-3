from petrified.widget import Widget
from petrified.datatypes import Boolean

class Text(Widget):

    pass


TextField = Text


class Password(Widget):

    pass


class SubmitButton(Widget):

    pass


class Hidden(Widget):

    pass


class TextArea(Widget):

    pass


class Selectbox(Widget):

    def __init__(self, title=None, options=[], desc=None, datatype=None, validators=[],
                 render_callback=None, *args, **kwargs):
        kwargs['options'] = options
        Widget.__init__(self, title, desc, datatype, validators, render_callback, *args, **kwargs)
        self.options = options or []


SelectBox = Selectbox


class Checkbox(Widget):

    def __init__(self, title=None, options=[], desc=None, datatype=None, validators=[],
                 render_callback=None, *args, **kwargs):
        Widget.__init__(self, title, desc, datatype, validators, render_callback, *args, **kwargs)
        self.datatype = Boolean()


class RadioButtons(Widget):

    def __init__(self, title=None, options=[], desc=None, datatype=None, validators=[],
                 render_callback=None, *args, **kwargs):
        Widget.__init__(self, title, desc, datatype, validators, render_callback, *args, **kwargs)
        self.options = options or []


class Radiobox(Widget):

    def __init__(self, title=None, options=[], desc=None, datatype=None, validators=[],
                 render_callback=None, *args, **kwargs):
        Widget.__init__(self, title, desc, datatype, validators, render_callback, *args, **kwargs)
        self.datatype = Boolean()
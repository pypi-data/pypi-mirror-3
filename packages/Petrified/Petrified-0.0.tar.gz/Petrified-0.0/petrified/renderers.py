def petrified_jinja2(mode, obj, context=None):
    from jinja2 import Environment, PackageLoader

    e = Environment(loader=PackageLoader('petrified', 'templates'))
    if mode == 'widget':
        t = e.get_template('%s.html' % obj.__class__.__name__.lower())
        return t.render(widget=obj, fragment=context)
    elif mode == 'form':
        t = e.get_template('form.html')
        return t.render(form=obj, content=context,
                        render_open=obj._render_open,
                        render_content=obj._render_content,
                        render_close=obj._render_close)
    return u''

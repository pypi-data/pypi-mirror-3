import inspect


def new_instance(instance):
    # if it's not a class then we can't really clone it...
    if not hasattr(instance, '__class__'):
        return instance

    def new(i):
        # has to be instance of a class, not a class itself
        if (not inspect.isclass(i)
                and hasattr(i, '__class__')
                and hasattr(i, 'new')):
            return i.new()
        else:
            return i

    kwargs = {}
    spec = inspect.getargspec(instance.__init__).args
    for arg in instance._spec:
        if arg not in spec:
            continue
        item = instance._spec[arg]
        if isinstance(item, list):
            cloned = []
            for item_ in item:
                cloned.append(new(item_))
        else:
            cloned = new(item)
        kwargs[arg] = cloned

    return instance.__class__(*[], **kwargs)

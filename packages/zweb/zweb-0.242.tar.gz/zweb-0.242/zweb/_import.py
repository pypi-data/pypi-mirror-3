import sys

def _import(name):
    components = name.split('.')
    mname = components[0]
    _mod = sys.modules.get(mname)

    if _mod:
        del sys.modules[mname]

    if len(components) == 1:
        mod = __import__(name, globals(), locals(), [], -1)
    else:
        mod = __import__(".".join(components[:-1]), globals(), locals(), [components[-1]], -1)

        for i in components[1:]:
            if hasattr(mod, i):
                mod = getattr(mod, i)
            else:
                mod = None
                break

    sys.modules[mname] = _mod
    return mod

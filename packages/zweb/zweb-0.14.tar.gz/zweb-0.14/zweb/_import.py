import sys

def _import(name):
    components = name.split('.')
    mname = components[0]
    _mod = sys.modules.get(mname)
    if mname in sys.modules:
        del sys.modules[mname]

    mod = __import__(name, globals(), locals(), [], -1)

    for comp in components[1:]:
        mod = getattr(mod, comp)

    if _mod:
        sys.modules[mname] = _mod

    return mod

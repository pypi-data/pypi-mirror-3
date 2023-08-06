#coding:utf-8


def _route_chain(args):
    handlers = []
    for i in args:
        prefix = i.__name__

        #import view.blog._install
        __import__('%s._install'%prefix)
        i = __import__(prefix, globals(), locals(), ['_route'], -1)
        handlers.extend(i._route.route.handlers)

    return handlers

def app_install(application, app_list):
    for domain , route_list in app_list:
        if not domain.startswith("."):
            domain = domain.replace('.', r"\.")
        application.add_handlers(
            domain,
            _route_chain(route_list)
        )


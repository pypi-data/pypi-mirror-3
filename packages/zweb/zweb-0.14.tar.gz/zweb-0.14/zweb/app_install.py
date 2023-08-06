#coding:utf-8

def _route_chain(args):
    handlers = []
    for i in args:
        name = i.__name__
        prefix = '%s.view'%name
        __import__('%s._install'%prefix)
        i = __import__(prefix, globals(), locals(), ['_route'], -1)
        handlers.extend(i._route.route.handlers)
    return handlers

def app_install(application, app_list):
    for domain , route_list in app_list:
        application.add_handlers(
            domain.replace('.', r"\."),
            _route_chain(route_list)
        )


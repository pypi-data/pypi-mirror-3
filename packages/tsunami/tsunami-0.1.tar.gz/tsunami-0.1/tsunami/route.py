import tornado.web
from . import uimodules as buildin_uimodules
from . import uimethods as buildin_uimethods

class Router(object):
    """
    decorates RequestHandlers and builds up a list of routables handlers

    Tech Notes (or "What the *@# is really happening here?")
    --------------------------------------------------------

    Everytime @route('...') is called, we instantiate a new route object which
    saves off the passed in URI.  Then, since it's a decorator, the function is
    passed to the route.__call__ method as an argument.  We save a reference to
    that handler with our uri in our class level routes list then return that
    class to be instantiated as normal.

    Later, we can call the classmethod route.get_routes to return that list of
    tuples which can be handed directly to the tornado.web.Application
    instantiation.

    Example
    -------

    route = Router(template_path='templates')

    @route('/some/path')
    class SomeRequestHandler(RequestHandler):
        def get(self):
            goto = self.reverse_url('other')
            self.redirect(goto)

    # so you can do myapp.reverse_url('other')
    @route('/some/other/path', name='other')
    class SomeOtherRequestHandler(RequestHandler):
        def get(self):
            goto = self.reverse_url('SomeRequestHandler')
            self.redirect(goto)

    route.redirect('/index/', '/')
    route.static('/static/', 'web/static', host='http://media.host.com')

    my_routes = route.routes

    HTML:

        in:
        <script src="{{url('/static/style.css')}}"></script>

        out:
        <script src="http://media.host.com/static/style.css"></script>
    """


    def __init__(self, template_path, ui_modules=[], ui_methods=[], host=''):
        self.routes = []
        self.host = host
        self.template_path = template_path
        self.include_host = False
        self.static_urls = []

        if ui_modules and not isinstance(ui_modules, list):
            ui_modules = [ui_modules]
        if ui_methods and not isinstance(ui_methods, list):
            ui_methods = [ui_methods]
        ui_methods.append(dict(url=self.url))

        ui_modules.append(buildin_uimodules)
        ui_methods.append(buildin_uimethods)

        self.ui_modules = ui_modules
        self.ui_methods = ui_methods

    def __call__(self, uri, name=None):
        """gets called when we class decorate"""
        def decorater(handler):
            self.routes.append(tornado.web.url(uri, handler, name=name))
            return handler
        return decorater

    def append(self, r):
        self.routes.append(r)

    def static(self, prefix, path, host=''):
        if prefix[-1] == '/':
            uri = prefix + '(.*)'
        else:
            uri = prefix + '/(.*)'
        self.routes.append((uri, tornado.web.StaticFileHandler, {'path':path}))
        self.static_urls.append((uri[:-4], host))

    def redirect(self, from_, to, name=None):
        self.routes.append(tornado.web.url(
            from_,
            tornado.web.RedirectHandler,
            dict(url=to),
            name=name ))

    def url(self, handler, path):
        if not self.include_host:
            return path

        for u in self.static_urls:
            if path.startswith(u[0]):
                return u[1] + path

        return self.host + path


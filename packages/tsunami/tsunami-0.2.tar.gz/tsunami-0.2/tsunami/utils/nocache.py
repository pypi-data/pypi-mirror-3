__author__ = 'tsangpo'





def nocache(method):
    def wrapped(handler, *args, **kwargs):
        handler.set_header('Cache-Control', 'no-cache, no-store')
        handler.set_header('Pragma', 'no-cache')
        handler.set_header('Expires', 'now')
        method(handler, *args, **kwargs)
    return wrapped





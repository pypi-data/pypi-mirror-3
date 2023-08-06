import json
import decimal
import logging



def json_default(o):
    if isinstance(o, decimal.Decimal):
        return str(o)
    else:
        raise TypeError()


def restrpc(method):
    def wrapped(self, *args, **kwargs):
        params = dict([(k,v[0]) for k,v in self.request.arguments.items()])
        logging.debug('[JOSN RPC Request]: %s', params)
        kwargs.update(params)
        result = method(self, *args, **kwargs)
        #logging.debug('[JSON RPC Response]: %s'%result)

        self.set_header('Cache-Control', 'no-cache, no-store')
        self.set_header('Pragma', 'no-cache')
        self.set_header('Expires', 'now')
        self.write(json.dumps(result, default=json_default))
    return wrapped





import logging
from tornado.web import HTTPError
from tornado.escape import json_decode, json_encode



def jsonrpc_post(self):
    jso = json_decode(self.request.body)
    method, params = jso['method'], jso['params']
    logging.debug('[JOSN RPC Request]: %s', jso)
    try:
        result = getattr(self, method)(*params)
        ret = dict(result=result)
    except HTTPError as httpe:
        if httpe.status_code==403:
            ret = dict(error='not login')
        else:
            logging.exception('jsonrpc error')
            error = str(httpe)
            ret = dict(error=error)
    except Exception as e:
        logging.exception('jsonrpc error')
        error = str(e)
        ret = dict(error=error)
    finally:
        self.set_header('Cache-Control', 'no-cache, no-store')
        self.set_header('Pragma', 'no-cache')
        self.set_header('Expires', 'now')
        self.set_header('Content-Type', 'text/json')
        self.write(json_encode(ret))
        logging.debug('[JSON RPC Response]: %s'%ret)



def jsonrpc(handler):
    handler.post = jsonrpc_post
    return handler


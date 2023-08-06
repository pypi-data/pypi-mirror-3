import json
import urllib
import logging
import tornado.web
import tornado.gen



class WeiboOAuthHandler(tornado.web.RequestHandler):

    CLIENT_ID = None
    CLIENT_SECRET = None

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        code = self.get_argument('code', None)
        redirect_uri = "http://%s%s"%(self.request.host, self.request.path)

        if code:
            form_data = urllib.urlencode({
                "grant_type": "authorization_code",
                "code": code,
                "client_id": self.CLIENT_ID,
                "client_secret": self.CLIENT_SECRET,
                "redirect_uri": redirect_uri
                })

            logging.debug('form_data: %s', form_data)
            request = tornado.httpclient.HTTPRequest("https://api.weibo.com/oauth2/access_token", method='POST', body=form_data)
            http_client = tornado.httpclient.AsyncHTTPClient()
            response = yield tornado.gen.Task(http_client.fetch, request)

            if response.error or not response.code==200:
                logging.warn('get access_token fail')
            else:
                res = json.loads(response.body)
                self.on_authenticated(res)
                return

        params = urllib.urlencode({
            "response_type": "code",
            "client_id": self.CLIENT_ID,
            "redirect_uri": redirect_uri,
            })
        self.redirect("https://api.weibo.com/oauth2/authorize?"+params)
        logging.debug("redirect to authorize page")


    # overwrite
    def on_authenticated(self, res):
        self.set_cookie('weibo_access_token', res['access_token'])
        self.redirect('/')



class WeiboClient(object):

    def __init__(self, access_token=None, source=None):
        self.access_token = access_token
        self.source = source

    def get(self, method, **params):
        return self.execute('GET', method, **params)

    def post(self, method, **params):
        return self.execute('POST', method, **params)

    def execute(self, httpmethod, method, **params):
        if self.access_token:
            params["access_token"] = self.access_token
        elif self.source:
            params["source"] = self.source

        if httpmethod=='GET':
            query = urllib.urlencode(params, True)
            url = "https://api.weibo.com/2/%s.json?%s"%(method, query)
            request = tornado.httpclient.HTTPRequest(url, method='GET')
        elif httpmethod=='POST':
            form_data = urllib.urlencode(params, True)
            url = "https://api.weibo.com/2/%s.json"%method
            request = tornado.httpclient.HTTPRequest(url, method='POST', body=form_data)

        def _task(request, callback):
            def _callback(response):
                if response.error:
                    res = (None, 'network error: %s'%response.error)
                else:
                    rsp = json.loads(response.body)
                    rsp = ObjectDict(rsp)
                    res = (rsp, None)
                callback(res)
            http_client = tornado.httpclient.AsyncHTTPClient()
            http_client.fetch(request, _callback)

        return tornado.gen.Task(_task, request)



class ObjectDict(dict):
    """Makes a dictionary behave like an object."""
    def __getattr__(self, name):
        name = name[:-1] if name[-1]=='_' else name
        try:
            o = self[name]
            if isinstance(o, dict):
                return ObjectDict(o)
            elif isinstance(o, list):
                return [ObjectDict(lo) if isinstance(lo, dict) else lo for lo in o]
            else:
                return o
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

import json
import urllib
import logging
import tornado.web
import tornado.gen


class UrlShortenClient(object):

    URL = 'http://126.am/api!shorten.action'

    def __init__(self, key):
        self.key = key

    def shorten(self, url):
        params = dict(key=self.key, longUrl=url)
        form_data = urllib.urlencode(params)
        request = tornado.httpclient.HTTPRequest(self.URL, method='POST', body=form_data)

        def _task(request, callback):
            def _callback(response):
                if response.error:
                    res = (None, 'network error: %s'%response.error)
                else:
                    rsp = json.loads(response.body)
                    res = (rsp['url'], None)
                callback(res)
            http_client = tornado.httpclient.AsyncHTTPClient()
            http_client.fetch(request, _callback)

        return tornado.gen.Task(_task, request)


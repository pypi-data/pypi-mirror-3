__author__ = 'tsangpo'

import logging
import tornado.web


'''
Request Headers

Must:
Expect: 100-continue
Transfer-Encoding: chunked

Must Not:
Content-Length: xxx


Handler:

class ChunkedRequestHandler(RequestHandler):

    @chunked
    def post(self):
        pass

'''

def chunked(method):
    def wrapper(handler, *args, **kwargs):
        ChunkedHandler(method)(handler, *args, **kwargs)
    return wrapper

class ChunkedHandler(object):

    def __init__(self, prepare):
        self.prepare = prepare

    def __call__(self, handler, *args, **kwargs):
        logging.debug('enter ChunkedHandler')
        expect = handler.request.headers.get('Expect', None)
        if expect and expect.lower() == '100-continue' and\
           not 'Content-Length' in handler.request.headers and\
           handler.request.headers.get('Transfer-Encoding', None) == 'chunked':

            self.prepare(handler, *args, **kwargs)

            handler._auto_finish = False
            self._stream = handler.request.connection.stream
            self._stream.write("HTTP/1.1 100 (Continue)\r\n\r\n")
            self.read_chunk_length()
            self.handler = handler
        else:
            logging.warn('non-chunked request: %s', handler.request.headers)
            raise tornado.web.HTTPError(500, "non-chunked request")

    def read_chunk_length(self):
        self._stream.read_until('\r\n', self._on_chunk_length)

    def read_chunk_data(self, size):
        self._stream.read_bytes(size + 2, self._on_chunk_data)

    def _on_chunk_length(self, data):
        assert data[-2:] == '\r\n', "chunk size ends with CRLF"
        chunk_length = int(data[:-2], 16)
        if chunk_length:
            self.read_chunk_data(chunk_length)
        else:
            self.handler.on_end()

    def _on_chunk_data(self, data):
        assert data[-2:] == '\r\n', "chunk data ends with CRLF"
        self.handler.on_chunk(data[:-2])
        self.read_chunk_length()



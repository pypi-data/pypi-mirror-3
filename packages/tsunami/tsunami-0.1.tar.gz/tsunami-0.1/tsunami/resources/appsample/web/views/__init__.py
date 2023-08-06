from tsunami.utils import RequestHandler
from .. import route



@route('/')
class IndexHandler(RequestHandler):

    def get(self):
        self.render('index.html')


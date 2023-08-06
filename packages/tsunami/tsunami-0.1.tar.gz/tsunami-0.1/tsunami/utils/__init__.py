__author__ = 'tsangpo'

import logging
import tornado.web
import tornado.escape
import tornado.template

from ..runtime import db
from .flash import FlashMixin
from .captcha import CaptchaMixin
from .paginator import PaginatorMixin
from .upload import UploadMinxin



class RequestHandler(tornado.web.RequestHandler, FlashMixin, CaptchaMixin, PaginatorMixin, UploadMinxin):

    def prepare(self):
        self.db = db.sessionmaker()
        self.ui['captcha_html'] = self.captcha_html

    def on_finish(self):
        try:
            self.db.close()
        except:
            logging.exception('db session close unnormal')

    def static_url(self, path, include_host=True):
        self.require_setting("static_path", "static_url")
        static_handler_class = self.settings.get(
            "static_handler_class", tornado.web.StaticFileHandler)

        if include_host is None:
            include_host = getattr(self, "include_host", False)

        if include_host:
            base = self.request.protocol + "://" + self.settings.get('static_url_host', self.request.host)
        else:
            base = ""
        return base + static_handler_class.make_static_url(self.settings, path)



#########
# patch tornado:
#   add datetime Type
#   add date Type
#   add None Type
#########


def generate(self, writer):
    writer.write_line("_tmp = %s" % self.expression, self.line)
    writer.write_line("if isinstance(_tmp, _string_types):"
                          " _tmp = _utf8(_tmp)", self.line)
    writer.write_line("elif isinstance(_tmp, datetime.datetime): "
                      "_tmp = _tmp.strftime('%Y-%m-%d %H:%M')", self.line)
    writer.write_line("elif isinstance(_tmp, datetime.date): "
                      "_tmp = _tmp.strftime('%Y-%m-%d')", self.line)
    writer.write_line("elif _tmp is None: pass", self.line)
    writer.write_line("else: _tmp = _utf8(str(_tmp))", self.line)
    if not self.raw and writer.current_template.autoescape is not None:
        # In python3 functions like xhtml_escape return unicode,
        # so we have to convert to utf8 again.
        writer.write_line("_tmp = _utf8(%s(_tmp))" %
                          writer.current_template.autoescape, self.line)
    writer.write_line("_append(_tmp)", self.line)

tornado.template._Expression.generate = generate

_xhtml_escape = tornado.escape.xhtml_escape
def xhtml_escape(value):
    if value is None: return ''
    return _xhtml_escape(value)
tornado.escape.xhtml_escape = xhtml_escape





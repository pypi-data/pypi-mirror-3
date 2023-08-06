import re
import tornado.web


class Paginator(tornado.web.UIModule):
    def render(self, p, templ='uimodules/paginator.html', url=None):
        if url is None:
            q = self.request.query
            if 'p=' in q:
                q = re.sub(r'(\&)?p=\d*', '', q)
            self.urltempl = self.request.path + '?' + q + '&p=${p}'
        else:
            self.urltempl = url
        return self.render_string(templ, p=p, url=self.url)

    def url(self, p):
        return self.urltempl.replace('${p}', str(p))



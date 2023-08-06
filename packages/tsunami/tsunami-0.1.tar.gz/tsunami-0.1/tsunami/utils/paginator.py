__author__ = 'tsangpo'




class PaginatorMixin(object):

    def get_pagination(self, query, limit=10):
        page = int(self.get_argument('p', '1'))
        total = query.count()
        paginator = Paginator(total, limit, page)
        objects = query.offset(paginator.offset).limit(paginator.limit).all()
        self.ui['paginator'] = paginator
        return objects



class Paginator(object):

    def __init__(self, total, size, page=1):
        self.total = total
        self.size = size
        self.page_total = 1 if total <= size else total/size+(1 if total%size else 0)
        self.page_num = min(page, self.page_total)
        self.is_first = self.page_num == 1
        self.is_last = self.page_num == self.page_total

        self.offset = (self.page_num - 1)*self.size
        self.limit = self.size

    @property
    def first(self):
        return 1

    @property
    def last(self):
        return self.total

    @property
    def prev(self):
        return self.page_num-1

    @property
    def next(self):
        return self.page_num+1

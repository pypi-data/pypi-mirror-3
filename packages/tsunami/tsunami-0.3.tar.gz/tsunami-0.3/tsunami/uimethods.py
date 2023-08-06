#!coding: utf-8
import urllib
import datetime


def url_with_query(self, **kwargs):
    params = dict([(k, v[0]) for k,v in self.request.arguments.items()])
    params.update(kwargs)
    return urllib.urlencode(params)


def relative_time(self, dtime):

    now = datetime.datetime.now().date()
    hour = dtime.hour
    date = dtime.date()

    days = (now - date).days
    if days==0:
        date = '今天'
    elif days==1:
        date = '昨天'
    elif days==2:
        date = '前天'
    elif days<6:
        date = '%s天前'%days
    elif now.year==date.year:
        date = date.strftime('%m月%d日')
    else:
        date = date.strftime('%y年%m月%d日')

    if hour<6:
        time = '凌晨'
    elif hour<12:
        time = '上午'
    elif hour<18:
        time = '下午'
    else:
        time = '晚上'

    return date + time

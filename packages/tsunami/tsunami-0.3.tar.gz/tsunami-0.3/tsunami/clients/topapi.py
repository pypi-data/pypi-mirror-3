#coding: utf-8
import time
import json
import hmac
import urllib
import hashlib
import logging
import datetime
import tornado.web
import tornado.gen
import tornado.httpclient
from tornado.escape import utf8



'''Examples:

@route('/taobaoke/auth/')
class TopAuthHandler(TopLoginHandler):

    isproduct = True
    app_key = TOP_APP_KEY
    app_secret = TOP_APP_SECRET

    def on_verify_ok(self, top_session, parameters):
        self.set_cookie('top_session', top_session)
        self.redirect('/tms2wb/')


@route('/taobaoke/cats/')
class CatsHandler(RequestHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        topclient = AsyncTopClient(TOP_APP_KEY, TOP_APP_SECRET, True)
        data, error = yield topclient.post(
            'taobao.itemcats.get',
            fields='cid,parent_cid,is_parent,name,sort_order',
            parent_cid='0',
            )
        self.render('test.html', test='%s, %s'%(data, error))

'''


class TopOAuthHandler(tornado.web.RequestHandler):
    app_key = ''
    app_secret = ''

    def get(self):
        try:
            top_parameters = self.get_argument('top_parameters').encode('utf-8')
            top_sign       = self.get_argument('top_sign').encode('utf-8')
            if self._verify_top_response(top_parameters, top_sign):
                top_parameters = self._parser_top_parameters(top_parameters)
                self.on_verify_ok(top_parameters)
                return
            else:
                logging.info('verify fail')
        except:
            logging.exception('not valid callback')

        redirect_uri = "http://%s%s"%(self.request.host, self.request.path)
        url_oauth = 'https://oauth.taobao.com/authorize?response_type=user&client_id=%s&redirect_uri=%s' %(self.app_key, redirect_uri)
        self.redirect(url_oauth)

    def _verify_top_response(self, top_parameters, top_sign):
        content = ''.join([top_parameters, self.app_secret])
        h = hashlib.md5(content).digest().encode('base64').strip()
        return h == top_sign.encode('utf-8')

    def _parser_top_parameters(self, parameters):
        params = dict([p.split('=') for p in parameters.decode('base64').split('&')])
        return params

    def on_verify_ok(self, top_parameters):
        pass


class MtopOAuthHandler(tornado.web.RequestHandler):

    APP_KEY = ''
    APP_SECRET = ''

    URL_CODE = 'https://oauth.taobao.com/authorize?response_type=code&view=wap&redirect_uri=%s&client_id=%s'
    URL_TOKEN = 'https://oauth.taobao.com/token'

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        redirect_uri = "http://%s%s"%(self.request.host, self.request.path)
        try:
            code = self.get_argument('code')
            params = dict(
                    grant_type='authorization_code',
                    code=code,
                    redirect_uri=redirect_uri,
                    client_id=self.APP_KEY,
                    client_secret=self.APP_SECRET,
                    view='wap',
                    )
            form_data = urllib.urlencode(params)
            request = tornado.httpclient.HTTPRequest(self.URL_TOKEN, method='POST', body=form_data)
            http_client = tornado.httpclient.AsyncHTTPClient()
            response = yield tornado.gen.Task(http_client.fetch, request)
            data = json.loads(response.body)
            logging.debug('got taobao oauth result: %s', data)
            self.on_verify_ok(data)
            if not self._finished:
                self.finish()
        except:
            url = self.URL_CODE % (redirect_uri, self.APP_KEY)
            self.redirect(url)

    def on_verify_ok(self, data):
        '''
            access_token 用户授权令牌，等价于Sessionkey
            token_type 授权令牌类型，暂做保留参数备用
            expires_in 授权令牌有效期，以秒为单位
            refresh_token 刷新令牌，当授权令牌过期时，可以刷新access_token，如果有获取权限则返回
            re_expires_in 刷新令牌的有效期
            hra_expires_in 高危API有效期（短授权相关）
            taobao_user_id 用户ID（子账号相关）
            taobao_user_nick 用户nick
            taobao_sub_user_id 子账号用户ID
            taobao_sub_user_nick 子账号用户nick
            mobile_token 无线端的ssid（对应于view=wap）
        '''
        pass


class TopLoginHandler(tornado.web.RequestHandler):

    isproduct = False
    app_key = ''
    app_secret = ''


    def get(self):
        try:
            top_appkey     = self.get_argument('top_appkey').encode('utf-8')
            top_parameters = self.get_argument('top_parameters').encode('utf-8')
            top_session    = self.get_argument('top_session').encode('utf-8')
            top_sign       = self.get_argument('top_sign').encode('utf-8')
            if self._verify_top_response(top_parameters, top_session, top_sign):
                top_parameters = self._parser_top_parameters(top_parameters)
                self.on_verify_ok(top_session, top_parameters)
                return
            else:
                logging.info('verify fail')
        except:
            logging.exception('not valid callback')

        url_sandbox = 'http://container.api.tbsandbox.com/container?appkey=' + self.app_key
        url_product = 'http://container.api.taobao.com/container?appkey=' + self.app_key
        if self.isproduct:
            self.redirect(url_product)
        else:
            self.redirect(url_sandbox)


    def _verify_top_response(self, top_parameters, top_session, top_sign):
        content = ''.join([self.app_key, top_parameters, top_session, self.app_secret])
        h = hashlib.md5(content).digest().encode('base64').strip()
        return h == top_sign.encode('utf-8')

    def _parser_top_parameters(self, parameters):
        params = dict([p.split('=') for p in parameters.decode('base64').split('&')])
        return params

    def on_verify_ok(self, top_session, top_parameters):
        pass



class TopClient(object):

    URL_PRODUCT = 'http://gw.api.taobao.com/router/rest'
    URL_SANDBOX = 'http://gw.api.tbsandbox.com/router/rest'

    def __init__(self, app_key, app_secret, isproduct=True, format='json'):
        if isproduct:
            self.url = self.URL_PRODUCT
        else:
            self.url = self.URL_SANDBOX
        self.app_key = app_key
        self.app_secret = app_secret

        self.rate = None

    def post(self, method, **params):
        params.update(
            method = method,
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            format = 'json',
            app_key = self.app_key,
            v = '2.0',
            )
        params = dict([(k,utf8(v)) for k,v in params.items() if v])
        params = self.sign_hmac(params)
        form_data = urllib.urlencode(params)
        #logging.debug('form_data: %s', form_data)
        request = tornado.httpclient.HTTPRequest(self.url, method='POST', body=form_data)

        def _task(request, callback):
            def _callback(response):
                if response.error:
                    res = (None, 'network error: %s'%response.error)
                else:
                    rsp = json.loads(response.body)
                    res = self.parse_response(rsp)
                callback(res)
            http_client = tornado.httpclient.AsyncHTTPClient()
            http_client.fetch(request, _callback)

        return tornado.gen.Task(_task, request)

    def set_sync_rate(self, per_min):
        self.rate = per_min
        self.acum = 0

    def check_sync_rate(self):
        if self.rate:
            self.acum += 1
            if self.acum == self.rate:
                time.sleep(60)
                self.acum = 0

    def post_sync(self, method, **params):
        self.check_sync_rate()
        logging.debug('topclient->%s(%s)', method, params)

        params.update(
            method = method,
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            format = 'json',
            app_key = self.app_key,
            v = '2.0',
            )
        params = dict([(k,utf8(v)) for k,v in params.items() if v])
        params = self.sign_hmac(params)
        form_data = urllib.urlencode(params)
        try:
            o = urllib.urlopen(self.url, form_data)
            if o.getcode()==200:
                rsp = json.loads(o.read())
                res = self.parse_response(rsp)
            else:
                res = (None, 'network error: %s'%o.info())
        except:
            res = (None, 'network error')
        finally:
            _, error = res
            if error:
                logging.warn('topclient post_sync error: %s', error)
            return res


    def sign_md5(self, params):
        params['sign_method'] = 'md5'
        content = ''.join(["%s%s" % (k, v) for k, v in sorted(params.items())])
        content = '%s%s%s' % (self.app_secret, content, self.app_secret)
        params['sign'] = hashlib.md5(content).hexdigest().upper()
        #logging.debug('params: %s\nsign content: %s', params, content)
        return params

    def sign_hmac(self, params):
        params['sign_method'] = 'hmac'
        content = ''.join(["%s%s" % (k, v) for k, v in sorted(params.items())])
        params['sign'] = hmac.new(self.app_secret, content).hexdigest().upper()
        #logging.debug('params: %s\nsign content: %s', params, content)
        return params

    def parse_response(self, rsp):
        data = None
        error = None
        if rsp.has_key('error_response'):
            error_code = rsp['error_response']['code']
            error = '[%s]%s' % (error_code, error_msg.get(error_code,u'未知错误'))
        else:
            data = rsp.values()[0]
            data = ObjectDict(data)
        return data, error



error_msg = {

    #系统级错误
    3:u'图片上传失败',
    4:u'用户调用次数超限',
    5:u'会话调用次数超限',
    6:u'合作伙伴调用次数超限',
    7:u'应用调用次数超限',
    8:u'应用调用频率超限',
    9:u'HTTP方法被禁止（请用大写的POST或GET）',
    10:u'服务不可用',
    11:u'开发者权限不足',
    12:u'用户权限不足',
    13:u'合作伙伴权限不足',
    15:u'远程服务出错',
    21:u'缺少方法名参数',
    22:u'不存在的方法名',
    23:u'非法数据格式',
    24:u'缺少签名参数',
    25:u'非法签名',
    26:u'缺少SessionKey参数',
    27:u'无效的SessionKey参数',
    28:u'缺少AppKey参数',
    29:u'非法的AppKey参数',
    30:u'缺少时间戳参数',
    31:u'非法的时间戳参数',
    32:u'缺少版本参数',
    33:u'非法的版本参数',
    34:u'不支持的版本号',
    40:u'缺少必选参数',
    41:u'非法的参数',
    42:u'请求被禁止',
    43:u'参数错误',

    #容器类错误
    100:u'授权码已经过期',
    101:u'授权码在缓存里不存在，一般是用同样的authcode两次获取sessionkey',
    103:u'appkey或者tid（插件ID）参数必须至少传入一个',
    104:u'appkey或者tid对应的插件不存在',
    105:u'插件的状态不对，不是上线状态或者正式环境下测试状态',
    106:u'没权限调用此app，由于插件不是所有用户都默认安装，所以需要用户和插件进行一个订购关系。',
    108:u'由于app有绑定昵称，而登陆的昵称不是绑定昵称，所以没权限访问。',
    109:u'服务端在生成参数的时候出了问题（一般是tair有问题）',
    110:u'服务端在写出参数的时候出了问题',
    111:u'服务端在生成参数的时候出了问题（一般是tair有问题）',

    #业务级错误
    501:u'语句不可索引',
    502:u'数据服务不可用',
    503:u'无法解释TBQL语句',
    504:u'需要绑定用户昵称',
    505:u'缺少参数',
    506:u'参数错误',
    507:u'参数格式错误',
    508:u'获取信息权限不足',
    540:u'交易统计服务不可用',
    541:u'类目统计服务不可用',
    542:u'商品统计服务不可用',
    550:u'用户服务不可用',
    551:u'商品服务不可用',
    552:u'商品图片服务不可用',
    553:u'商品更新服务不可用',
    554:u'商品删除失败',
    555:u'用户没有订购图片服务',
    556:u'图片URL错误',
    557:u'商品视频服务不可用',
    560:u'交易服务不可用',
    561:u'交易服务不可用',
    562:u'交易不存在',
    563:u'非法交易',
    564:u'没有权限添加或更新交易备注',
    565:u'交易备注超出长度限制',
    566:u'交易备注已经存在',
    567:u'没有权限添加或更新交易信息',
    568:u'交易没有子订单',
    569:u'交易关闭错误',
    570:u'物流服务不可用',
    571:u'非法的邮费',
    572:u'非法的物流公司编号',
    580:u'评价服务不可用',
    581:u'添加评价服务错误',
    582:u'获取评价服务错误',
    590:u'店铺服务不可用',
    591:u'店铺剩余推荐数 服务不可用',
    592:u'卖家自定义类目服务不可用',
    594:u'卖家自定义类目添加错误',
    595:u'卖家自定义类目更新错误',
    596:u'用户没有店铺',
    597:u'卖家自定义父类目错误',
    601:u'用户不存在',
    611:u'产品数据格式错误',
    612:u'产品ID错误',
    613:u'删除产品图片错误',
    614:u'没有权限添加产品',
    615:u'收货地址服务不可用',
    620:u'邮费服务不可用',
    621:u'邮费模板类型错误',
    622:u'缺少参数：post, express或ems',
    623:u'邮费模板参数错误',
    630:u'收费服务不可用',
    650:u'退款服务不可用',
    651:u'非法的退款编号',
    670:u'佣金服务不可用',
    671:u'佣金交易不存在',
    672:u'淘宝客报表服务不可用',
    673:u'备案服务不可用',
    674:u'应用服务不可用',
    710:u'淘宝客服务不可用',
    900:u'远程连接错误',
    901:u'远程服务超时',
    902:u'远程服务错误',
}



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






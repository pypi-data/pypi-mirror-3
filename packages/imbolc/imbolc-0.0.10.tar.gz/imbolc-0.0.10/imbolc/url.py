# -*- coding: utf-8 -*-
'''
Объектная обёртка над urllib
Пример:
    res = query('dev.pooqle.com', ref='ya.ru', get=dict(a=1), post=dict(b=2))
    print res.url   # урл может отличаться от запрашиваемого в случае редиректа
    print res.code
    print res.headers
    print res.body  # запрос тела страницы произойдёт только тут
    print bool(res) # True - если код == 200 и загрузилось body
'''
import os
import re
import sys
import random
import urllib
import urllib2
import httplib
import logging
from gzip import GzipFile
from cookielib import CookieJar, Cookie
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
try:
    import cPickle as pickle
except ImportError:
    import pickle
import simplejson as json

try:
    import leaf
except ImportError:
    print 'warning: module not found: leaf'

from decorators import cached_property


url = sys.modules[__name__]  # for auto-import

RE_CONTENT_TYPE_TAG = re.compile(r'<meta[^>]+http-equiv\s*=\s*["\']Content-Type[^>]+', re.I|re.S)
RE_CHARSET = re.compile(r'charset\s*=\s*([-_a-z0-9]+)', re.I)


http_handler = urllib2.HTTPHandler()
http_handler.set_http_debuglevel(1)
try:
    https_handler = urllib2.HTTPSHandler()
    https_handler.set_http_debuglevel(1)
except AttributeError:
    pass
#~ logger = logging.getLogger()
#~ logger.addHandler(logging.StreamHandler(sys.stdout))
#~ logger.setLevel(logging.NOTSET)


def main():
    import doctest
    doctest.testmod()
    
    return
    url = 'dev.pooqle.com'

    res = load(url,
        #~ debug=1, 
        #~ log_dir='var/om.url.logs'
        )
    print res.code
    print res.body
    print res.load_defaults['user_agent']
    #~ res.load(url)
    #~ print res.code
    #~ print res.url
    #~ print res.cookies



def load(url, size=None, get=None, post=None, compress=True,
        headers=None, cookies=None, user_agent=None, referer=None,
        proxy=None, proxy_type='http',
        charset='utf-8', safe=True, debug=False, log_dir=None,
        _req_cnt=0):
    '''
    Получает страницу, с любым статусом
        **size = ограничение на размер скачиваемой части страницы в байтах
        **get = словарь или список пар переменных GET-запроса
        **post = словарь или список пар переменных POST-запроса
        **headers = словарь заголовков
        **cookies = StringCookieJar object or res.cj.dumps() string
        **user_agent = юзерагент
        **referer = реферер
        **proxy = прокси в виде user:passwd@host:port
        **proxy_type = тип прокси
        **compress = получение страниц сжатыми по возможности
        **safe = перехват всех исключений, возвращает Response(code=0, body='')
        **debug = лог запросов в консоль
        **log_dir = папка для сохранения страниц в debug-режиме
    '''
    url = url_fix(url, charset)
    # add get-params
    if get:
        if '#' in url:
            pos = url.find('#')
            url, end = url[:pos], url[pos:]
        else:
            end = ''
        sep = '&' if '?' in url else '?'
        url += sep + urllib.urlencode(encoded_unique_items(get)) + end
    q = {'url': url}
    if post:
        q['data'] = urllib.urlencode(encoded_unique_items(post))
    req = urllib2.Request(**q)
    if headers:
        for item in encoded_unique_items(headers):
            req.add_header(*item)
    if user_agent is None:
        user_agent = str(random.choice(USER_AGENTS)())
    req.add_header('User-agent', user_agent)
    if referer:
        req.add_header('Referer', url_fix(referer))
    if isinstance(cookies, StringCookieJar):
        cookies = cookies
    if isinstance(cookies, basestring):
        cookies = StringCookieJar(cookies)
    elif isinstance(cookies, dict):
        cj = StringCookieJar()
        for name, value in cookies.iteritems():
            cookie = Cookie(
                version=0,
                name=name,
                value=value,
                port=None,
                port_specified=False,
                domain=req.get_host(),
                domain_specified=False,
                domain_initial_dot=False,
                path='/',
                path_specified=True,
                secure=False,
                expires=None,
                discard=True,
                comment=None,
                comment_url=None,
                rest={'HttpOnly': None},
                rfc2109=False
            )
            cj.set_cookie(cookie)
        cookies = cj
    else:
        assert False, 'cookies must be StringCookieJar, dict or basestring type'
    handlers = [urllib2.HTTPCookieProcessor(cookies)]
    if compress:
        req.add_header("Accept-Encoding", "gzip")
    _req_cnt += 1
    if debug:
        print '<<< [%02i] %s %s' % (_req_cnt, 'POST' if post else 'GET', url)
        handlers.extend([http_handler, https_handler])
    if proxy:
        if '@' in proxy:
            schema = '%s://' % proxy_type
            if proxy.startswith(schema):
                proxy = proxy[len(schema):]
            proxy_user, proxy_host = proxy.split('@')
            proxy_passwd = None
            if ':' in proxy_user:
                proxy_user, proxy_passwd = proxy_user.split(':')
            proxy_handler = urllib2.ProxyHandler({proxy_type: proxy_host})
            proxy_auth_handler = urllib2.ProxyBasicAuthHandler(ProxyPasswordMgr())
            proxy_auth_handler.add_password(None, None, proxy_user, proxy_passwd)
            handlers.extend([proxy_handler, proxy_auth_handler])
        else:
            req.set_proxy(proxy, proxy_type)
    opener = urllib2.build_opener(*handlers)
    if safe:
        try:
            conn = opener.open(req)
        except urllib2.HTTPError, e:
            conn = e
        except Exception, ex:
            conn = StringIO('')
    else:
        conn = opener.open(req)
    load_defaults = {
        'compress': compress,
        'cookies': cookies,
        'user_agent': user_agent,
        'referer': getattr(conn, 'url', None),
        'proxy': proxy,
        'proxy_type': proxy_type,
        'safe': safe,
        'debug': debug,
        'log_dir': log_dir,
        '_req_cnt': _req_cnt,
    }
    return Response(conn, getattr(conn, 'code', 0), size, load_defaults)


class Response(object):
    body_load_error = False
    
    def __init__(self, conn, code, size, load_defaults):
        self.conn = conn
        self.size = size
        self.code = code
        self.load_defaults = load_defaults
        if self.load_defaults['log_dir']:
            self._log_page()
        
    def __nonzero__(self):
        self.body
        return self.code == 200 and not self.body_load_error

    def load(self, url, **kwargs):
        for k, v in self.load_defaults.iteritems():
            if k not in kwargs:
                kwargs[k] = v
        return load(url, **kwargs)

    @cached_property
    def url(self):
        return self.load_defaults['referer']

    @cached_property
    def headers(self):
        return self.conn.headers.dict if self.code else {}
    
    @cached_property
    def cookies(self):
        return self.load_defaults['cookies']
    
    @cached_property
    def body(self):
        try:
            if 'gzip' in self.headers.get('content-encoding', ''):
                ret = GzipFile(
                    fileobj=StringIO(self.conn.read(self.size))).read()
            else:
                ret = self.conn.read(self.size) if self.code else ''
        except Exception:
            if not self.load_defaults['safe']:
                raise
            self.body_load_error = True
            ret = ''
        return ret
            
    @cached_property
    def ubody(self):
        return self.body.decode(self.charset)
        
    @cached_property
    def dom(self):
        return leaf.parse(self.body)
    
    @cached_property
    def json(self):
        return json.loads(self.body)
    
    @cached_property
    def charset(self):
        enc = 'utf-8'
        # ищем в заголовках
        hdr = self.headers.get('Content-Type', '').lower()
        try:
            enc = hdr.split('charset')[1].split('=')[1].strip().lower()
        except IndexError:
            # в заголовках пусто, ищем в метатеге
            match = RE_CONTENT_TYPE_TAG.search(self.body)
            if match:
                match = RE_CHARSET.search(match.group(0))
                if match:
                    enc = match.group(1).lower()
        return enc
        
    def form(self, items=None, form_num=None):
        '''
        *items  : dict or items данных для заполнения формы,
        return form dict
        '''
        items = items or ()
        if not isinstance(form_num, (int, type(None))):
            form = form_num
        else:
            forms = self.dom.forms
            if form_num is None:
                if len(forms) > 1:
                    # form is not set, choose the form of maximum size
                    forms.sort(key=lambda x: -len(x.fields))
                form = forms[0]
            else:
                form = forms[form_num]
        ret = dict(form.form_values())
        ret.update(dict(items) if not isinstance(items, dict) else items)
        return ret
        
    def _log_page(self):
        dir = self.load_defaults['log_dir']
        cnt = self.load_defaults['_req_cnt']
        if cnt == 1:
            # prepare log directory
            if not os.path.exists(dir):
                os.makedirs(dir)                
            for fn in os.listdir(dir):
                full_fn = os.path.join(dir, fn)
                if os.path.isfile(full_fn) and fn.split('.')[0].isdigit():
                    os.remove(full_fn)
        fn_tpl = os.path.join(dir, '%02i.%%s' % cnt)
        open(fn_tpl % 'hdrs.txt', 'w').write(str(self.conn.headers))
        ct = self.headers.get('content-type', '').lower()
        ext = {
            'image/jpeg': 'jpg',
            'image/gif': 'gif',
            'image/png': 'png',
        }.get(ct, 'html')
        open(fn_tpl % ext, 'w').write(self.body)                    


class ProxyPasswordMgr:
    def __init__(self):
        self.user = self.passwd = None
    def add_password(self, realm, uri, user, passwd):
        self.user = user
        self.passwd = passwd
    def find_user_password(self, realm, authuri):
        return self.user, self.passwd


class StringCookieJar(CookieJar):
    def __init__(self, dump=None, policy=None):
        CookieJar.__init__(self, policy)
        if dump:
            if isinstance(dump, unicode):
                dump = dump.encode('utf-8')
            self._cookies = pickle.loads(dump)

    def dumps(self):
        return pickle.dumps(self._cookies)


def encoded_unique_items(items_or_dict, charset='utf-8'):
    if isinstance(items_or_dict, dict):
        items_or_dict = items_or_dict.iteritems()
    ret = {}
    for k, v in items_or_dict:
        ret[(
            k.encode(charset) if isinstance(k, unicode) else k,
            v.encode(charset) if isinstance(v, unicode) else v
        )] = True
    return ret.keys()


def url_fix(url, charset='utf-8'):
    '''
        Fix no path:
            >>> url_fix('host.com')
            'http://host.com/'
            
            >>> url_fix('host.com?a=b')
            'http://host.com/?a=b'
            
            >>> url_fix('host.com#a=b')
            'http://host.com/#a=b'
            
            >>> url_fix('https://host.com?a=b&a=c#id')
            'https://host.com/?a=b&a=c#id'
            
        Fix spaces:
            >>> url_fix('en.wikipedia.org/wiki/Doorway page')
            'http://en.wikipedia.org/wiki/Doorway%20page'
            
        Fix unicode:
            >>> url_fix('ru.wikipedia.org/wiki/Питон'.decode('utf-8'))
            'http://ru.wikipedia.org/wiki/%D0%9F%D0%B8%D1%82%D0%BE%D0%BD'
        
        Fix idna host:
            >>> url_fix('рег.рф/aaa/'.decode('utf-8'))
            'http://xn--c1ad6a.xn--p1ai/aaa/'
    '''
    url = url.strip()
    if not url.startswith(('http://', 'https://', 'ftp://', 'ftps://')):
        # no schema
        url = 'http://' + url
    if '/' not in url.split('//')[-1]:
        # no path
        frags = [url.find(sep) for sep in ('?', '#') if sep in url]
        if frags:
            x = min(frags)
            host, qs = url[:x], url[x:]
        else:
            host, qs = url, ''
        url = host + '/' + qs
    if isinstance(url, unicode):
        url = url.encode(charset)
    host = url.split('//', 1)[1].split('/', 1)[0]
    if not host.replace('.', '').replace('-', '').isalnum():
        # idn
        host = host.decode('utf-8').encode('idna')
        schema = url.split('//', 1)[0]
        uri = url.split('/', 3)[-1]
        url = '%s//%s/%s' % (schema, host, uri)
    url = urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
    return url


class RNDDict(object):
    TPL = None
    DATA = {}
    
    def __getitem__(self, key):
        return random.choice(self.DATA[key])

    def __str__(self):
        return self.TPL % self


class UAOpera(RNDDict):
    # http://www.useragentstring.com/pages/Opera/
    TPL = '%(name)s (%(os)s; U; %(lang)s) Presto/%(presto)s Version/%(ver)s'
    DATA = {
        'name': ['Opera/9.80'],
        'os': ['Windows NT 6.1', 'Windows NT 6.0', 'Windows NT 5.1'],
        'lang': ['en', 'en-US', 'ru', 'de'],
        'presto': ['2.8.99', '2.8.131', '2.7.62'],
        'ver': ['11.10', '11.01'],
    }

class UAFirefox(RNDDict):
    TPL = '%(name)s (Windows; U; %(os)s; %(lang)s) Gecko/%(engine)s Firefox/%(ver)s'
    DATA = {
        'name': ['Mozilla/5.0'],
        'os': ['Windows NT 6.1', 'Windows NT 6.0', 'Windows NT 5.1'],
        'lang': ['en', 'en-US', 'ru', 'de'],
        'engine': ['20100401', '20091204', '20090402', '20091124', '20100824', '20100722'],
        'ver': ['4.0', '3.8', '3.6.9', '3.6.8', '3.6.7', '3.6.6', '3.6.5', '3.6.3', '3.6.2', '3.6.16', '3.6.15', '3.6.14', '3.6.13', '3.6.12',],
        'rv': ['1.9.2.8', '1.9.2.3', '1.9.2.9', '', '', ],
    }

class UAChrome(RNDDict):
    TPL = '%(name)s (%(os)s) AppleWebKit/%(engine)s (KHTML, like Gecko) Chrome/%(ver)s'
    DATA = {
        'name': ['Mozilla/5.0'],
        'os': ['Windows NT 6.1', 'Windows NT 6.0', 'Windows NT 5.1'],
        'engine': ['534.25', '534.24'],
        'ver': ['12.0.706.0 Safari/534.25', '12.0.702.0 Safari/534.24', '11.0.699.0 Safari/534.24', '11.0.697.0 Safari/534.24'],
    }

class UAIE8(RNDDict):
    TPL = '%(ua)s'
    DATA = {
        'ua': [s.strip() for s in '''
            Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.2; Trident/4.0; Media Center PC 4.0; SLCC1; .NET CLR 3.0.04320)
            Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 1.1.4322)
            Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727)
            Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)
            Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.0; Trident/4.0; InfoPath.1; SV1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 3.0.04506.30)
            Mozilla/5.0 (compatible; MSIE 7.0; Windows NT 5.0; Trident/4.0; FBSMTWB; .NET CLR 2.0.34861; .NET CLR 3.0.3746.3218; .NET CLR 3.5.33652; msn OptimizedIE8;ENUS)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; Media Center PC 6.0; InfoPath.2; MS-RTC LM 8)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; Media Center PC 6.0; InfoPath.2; MS-RTC LM 8
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; Media Center PC 6.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET4.0C)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; InfoPath.3; .NET4.0C; .NET4.0E; .NET CLR 3.5.30729; .NET CLR 3.0.30729; MS-RTC LM 8)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; InfoPath.2)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; Zune 3.0)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; msn OptimizedIE8;ZHCN)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; MS-RTC LM 8; InfoPath.3; .NET4.0C; .NET4.0E) chromeframe/8.0.552.224
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; MS-RTC LM 8; .NET4.0C; .NET4.0E; Zune 4.7; InfoPath.3)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; MS-RTC LM 8; .NET4.0C; .NET4.0E; Zune 4.7)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; MS-RTC LM 8)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; Zune 4.0)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E; MS-RTC LM 8; Zune 4.7)
        '''.split('\n') if s.strip()],
    }

USER_AGENTS = [UAOpera, UAFirefox, UAChrome, UAIE8]


def decode_qs(qs, charset='utf-8'):
    '''
    Переводим строку запроса в переменные post/get запроса.
        *qs - строка запроса
        **out_enc - кодировка возвращаемой строки
    '''
    import cgi
    return (u'post=(\n%s\n)' % 
        ',\n'.join(["    (%s, u'%s')" % ("'%s'" % k.strip(),
            v[0].strip().decode(charset))
        for k, v in cgi.parse_qs(qs, keep_blank_values=True).items()]
        )).encode('utf-8')



if __name__ == "__main__":
    main()
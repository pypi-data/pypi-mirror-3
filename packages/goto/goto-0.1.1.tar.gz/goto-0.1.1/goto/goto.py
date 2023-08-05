#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Goto - urllib object wrapper'''
import os
import re
import sys
import random
import urllib
import urllib2
import httplib
from gzip import GzipFile
import zlib
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from utils import url_fix, cached_property, extras, encoded_unique_items 
from utils import cj_dumps,  cj_from_dump, cj_from_dict, cj_from
from useragents import USER_AGENTS

RE_CONTENT_TYPE_TAG = re.compile(
    r'<meta[^>]+http-equiv\s*=\s*["\']Content-Type[^>]+', re.I|re.S)
RE_CHARSET = re.compile(r'charset\s*=\s*([-_a-z0-9]+)', re.I)


http_handler = urllib2.HTTPHandler()
http_handler.set_http_debuglevel(1)
try:
    https_handler = urllib2.HTTPSHandler()
    https_handler.set_http_debuglevel(1)
except AttributeError:
    pass


def goto(url, size=None, get=None, post=None, compress=True,
        headers=None, cookies=None, user_agent=None, referer=None,
        proxy=None, proxy_type='http',
        charset='utf-8', safe=True, debug=False, log_dir=None,
        _req_cnt=0):
    '''
    Load page
        **size = max loaded part of page in bytes
        **get = GET vars dict or item list
        **post = POST vars dict or item list
        **headers = headers dict
        **cookies = dict or StringCookieJar object or str dump
        **user_agent = usragent
        **referer = referer
        **proxy = proxy in the format 'user:passwd@host:port'
        **proxy_type = proxy type
        **compress = use gzip if it possible
        **safe = if has exception, return Response(code=0, body='')
        **debug = debug info to the terminal
        **log_dir = dir for the pages log
    '''
    url = url_fix(url, charset)
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
    cookies = cj_from(cookies)
    handlers = [urllib2.HTTPCookieProcessor(cookies)]
    if compress:
        if size:
            assert 0, 'size and compress options is not compatible'
        req.add_header('Accept-Encoding', 'gzip')
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

    def goto(self, url, **kwargs):
        for k, v in self.load_defaults.iteritems():
            if k not in kwargs:
                kwargs[k] = v
        return goto(url, **kwargs)

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
    def cookies_dump(self):
        return cj_dumps(self.cookies)
    
    @cached_property
    def body(self):
        data = ''
        if self.code:
            try:
                data = self.conn.read(self.size)
                if 'gzip' in self.headers.get('content-encoding', ''):
                    data = GzipFile(fileobj=StringIO(data)).read()
            except Exception, e:
                if not self.load_defaults['safe']:
                    raise
                self.body_load_error = e
        return data
            
    @cached_property
    def ubody(self):
        return self.body.decode(self.charset)
        
    @cached_property
    def dom(self):
        return extras.leaf.parse(self.body)
    
    @cached_property
    def json(self):
        return extras.json.loads(self.body)
    
    @cached_property
    def mime(self):
        ret = self.headers.get('content-type')
        if ret:
            ret = ret.lower().split(';')[0]
        return ret
    
    @cached_property
    def charset(self):
        enc = 'utf-8'
        hdr = self.headers.get('content-type', '').lower()
        try:
            enc = hdr.split('charset')[1].split('=')[1].strip()
        except IndexError:
            match = RE_CONTENT_TYPE_TAG.search(self.body)
            if match:
                match = RE_CHARSET.search(match.group(0))
                if match:
                    enc = match.group(1).lower()
        return enc
        
    def form(self, items=None, form_num=None):
        '''
        *items  : dict or items form data,
        **form_num  = form or form number
        '''
        items = items or ()
        if not isinstance(form_num, (int, type(None))):
            form = form_num
        else:
            forms = self.dom.forms
            if form_num is None:
                if len(forms) > 1:
                    # form is not set, choose the form with maximum size
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



if __name__ == "__main__":
    import doctest
    doctest.testmod()

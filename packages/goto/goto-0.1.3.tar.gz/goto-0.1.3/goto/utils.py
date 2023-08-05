#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
from cookielib import CookieJar, Cookie


class cached_property(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, instance, owner):
        value = self.f(instance)
        setattr(instance, self.f.__name__, value)
        return value


class cached_classmethod(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, instance, owner):
        value = self.f(owner)
        setattr(owner, self.f.__name__, value)
        return value


class extras(object):
    '''Lazy import extra modules'''
    
    @cached_classmethod
    def json(cls):
        try:
            import simplejson as json
        except ImportError:
            import json
        return json

    @cached_classmethod
    def leaf(cls):
        import leaf
        return leaf

    @cached_classmethod
    def pickle(cls):
        try:
            import cPickle as pickle
        except ImportError:
            import pickle
        return pickle

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

def decode_qs(qs, charset='utf-8'):
    '''qs to query dict'''
    import cgi
    return (u'post=(\n%s\n)' % 
        ',\n'.join(["    (%s, u'%s')" % ("'%s'" % k.strip(),
            v[0].strip().decode(charset))
        for k, v in cgi.parse_qs(qs, keep_blank_values=True).items()]
        )).encode('utf-8')

def cj_dumps(cj, dumper='json'):
    return extras.pickle.dumps(cj._cookies) 

def cj_from_dump(dump, dumper='json'):
    cj = CookieJar()
    if isinstance(dump, unicode):
        dump = dump.encode('utf-8')
    cj._cookies = extras.pickle.loads(dump)
    return cj

def cj_from_dict(cookies_dict, req):
    cj = CookieJar()
    for name, value in cookies_dict.iteritems():
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
    return cj

def cj_from(cookies, req):
    if isinstance(cookies, CookieJar):
        return cookies
    if cookies is None:
        return CookieJar()
    if isinstance(cookies, dict):
        return cj_from_dict(cookies, req)
    if isinstance(cookies, basestring):
        return cj_from_dump(cookies)
    assert False, 'cookies must be StringCookieJar, dict or basestring type'

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


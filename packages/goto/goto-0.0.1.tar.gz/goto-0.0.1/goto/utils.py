#!/usr/bin/env python
# -*- coding: utf-8 -*-



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



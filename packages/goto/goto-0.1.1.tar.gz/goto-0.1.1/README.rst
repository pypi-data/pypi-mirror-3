goto
====

Installation
------------
::

    $ pip install goto

Usage
-----
::

    >>> import goto
    >>> page = goto('рег.рф')
    >>> page.code
    200
    >>> page.body[:25]
    '\n\n\n<!DOCTYPE html PUBLIC '
    >>> page.mime
    'text/html'
    >>> page.charset
    'windows-1251'
    >>> page.ubody[:25]
    u'\n\n\n<!DOCTYPE html PUBLIC '
    >>> page.headers['content-encoding']
    'gzip'
    >>> str(page.cookies)[:20]
    '<cookielib.CookieJar'


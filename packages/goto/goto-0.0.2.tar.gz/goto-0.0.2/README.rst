odbm
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

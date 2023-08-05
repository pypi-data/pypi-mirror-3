# encoding=UTF-8
# Copyright © 2010 Jakub Wilk <jwilk@jwilk.net>
#
# This package is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This package is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

import contextlib
import locale
import os
import re
import sys
import traceback

from nose.tools import *

try:
    locale.LC_MESSAGES
except AttributeError:
    # A non-POSIX system.
    locale.LC_MESSAGES = locale.LC_ALL

locale_encoding = locale.getpreferredencoding()
if locale_encoding == 'ANSI_X3.4-1968':
    locale_encoding = 'UTF-8'

py3k = sys.version_info >= (3, 0)

if py3k:
    def u(s):
        return s
else:
    def u(s):
        return s.decode('UTF-8')

if py3k:
    def b(s):
        return s.encode('UTF-8')
else:
    def b(s):
        return s

if py3k:
    def L(i):
        return i
else:
    def L(i):
        return long(i)

if py3k:
    def cmp(x, y):
        if x == y:
            return 0
        if x < y:
            return -1
        if x > y:
            return 1
        assert 0

if py3k:
    def blob(*args):
        return bytes(args)
else:
    def blob(*args):
        return ''.join(map(chr, args))

if py3k:
    from io import StringIO
else:
    from cStringIO import StringIO

if py3k:
    unicode = str

if py3k:
    maxsize = sys.maxsize
else:
    maxsize = sys.maxint

@contextlib.contextmanager
def raises(exc_type, string=None, regex=None):
    if string is None and regex is None:
        string = '' # XXX
    assert (string is None) ^ (regex is None)
    try:
        yield None
    except exc_type:
        _, exc, _ = sys.exc_info()
        exc_string = str(exc)
        if string is not None:
            if string != exc_string:
                message = '%r != %r' % (exc_string, string)
                raise AssertionError(message)
        else:
            if not re.match(regex, exc_string):
                message = '%r !~ %r' % (exc_string, regex)
                raise AssertionError(message)
    else:
        message = '%s was not raised' % exc_type.__name__
        raise AssertionError(message)

@contextlib.contextmanager
def amended_locale(**kwargs):
    old_locale = locale.setlocale(locale.LC_ALL)
    try:
        for category, value in kwargs.items():
            category = getattr(locale, category)
            locale.setlocale(category, value)
        yield
    finally:
        locale.setlocale(locale.LC_ALL, old_locale)

def assert_repr(self, expected):
    return assert_equal(repr(self), expected)

# vim:ts=4 sw=4 et

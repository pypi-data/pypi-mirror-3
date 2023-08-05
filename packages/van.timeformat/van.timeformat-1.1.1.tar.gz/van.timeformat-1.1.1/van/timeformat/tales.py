##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""ZPT integration for time formatting"""

from van.timeformat import timefmt, ltimefmt

from zope.tales.expressions import PathExpr

class LocalTimeFormatExpr(object):

    def __init__(self, name, expr, engine):
        self._name = name
        self._s = expr
        cat, length = expr.split(':')[:2]
        self._category = cat.strip()
        self._length = length.strip()
        var_expr = ':'.join(expr.split(':')[2:])
        self._var_expr = engine.compile(var_expr)

    def __call__(self, econtext):
        locale = econtext.vars['request'].locale
        ob = self._var_expr(econtext)
        return ltimefmt(ob, locale=locale, category=self._category, length=self._length)

    def __str__(self):
        return '%s expression (%s)' % (self._name, self._s)

    def __repr__(self):
        return '<LocaliTimeFormatExpr %s:%s>' % (self._name, self._s)


class TimeFormatExpr(object):

    def __init__(self, name, expr, engine):
        self._name = name
        self._s = expr
        self._format = expr.split(':')[0].strip()
        var_expr = ':'.join(expr.split(':')[1:])
        self._var_expr = engine.compile(var_expr)

    def __call__(self, econtext):
        ob = self._var_expr(econtext)
        return timefmt(ob, format=self._format)

    def __str__(self):
        return '%s expression (%s)' % (self._name, self._s)

    def __repr__(self):
        return '<TimeFormatExpr %s:%s>' % (self._name, self._s)

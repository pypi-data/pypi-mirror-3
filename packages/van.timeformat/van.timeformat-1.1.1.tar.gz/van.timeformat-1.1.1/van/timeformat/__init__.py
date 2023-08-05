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
from datetime import datetime, date
from zope.component import getUtility

from van.timeformat.interfaces import ITimeFormat

def timefmt(obj, format='iso'):
    if obj is None:
        return None
    assert isinstance(obj, date), "format only accepts date or datetime objects"
    if format == 'iso':
        s = obj.isoformat()
    else:
        format = getUtility(ITimeFormat, name=format).format
        format = format.encode('utf-8')
        s = obj.strftime(format).decode('utf-8')
    return unicode(s)

def ltimefmt(obj, locale, category=None, length=None):
    if obj is None:
        return None
    if category is None:
        if isinstance(obj, datetime):
            category = 'dateTime'
        elif isinstance(obj, date):
            category = 'date'
    formatter = locale.dates.getFormatter(category, length=length)
    return formatter.format(obj)

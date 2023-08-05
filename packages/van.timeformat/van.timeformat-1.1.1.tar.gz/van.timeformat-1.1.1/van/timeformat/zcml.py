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
from zope.interface import implements
from zope.component.zcml import utility
from zope.schema import TextLine

from van.timeformat.interfaces import ITimeFormat

class TimeFormat:

    implements(ITimeFormat)

    def __init__(self, format):
        self.format = format

class ITimeFormatDirective(ITimeFormat):

    name = TextLine(title=u"The name of the time format")

def time_format(context, name, format):
    format = TimeFormat(format)
    utility(context, component=format, name=name, provides=ITimeFormat)

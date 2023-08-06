### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
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


# import standard packages
import string

# import Zope3 interfaces
from zope.schema.interfaces import ITextLine

# import local interfaces

# import Zope3 packages
from zope.interface import implements
from zope.schema import TextLine
from zope.schema._bootstrapfields import InvalidValue

# import local packages

from ztfy.utils import _


class StringLine(TextLine):
    """String line field"""

    _type = str

    def fromUnicode(self, value):
        return str(value)


class IColorField(ITextLine):
    """Marker interface for color fields"""


class ColorField(TextLine):
    """Color field"""

    implements(IColorField)

    def __init__(self, *args, **kw):
        super(ColorField, self).__init__(max_length=6, *args, **kw)

    def _validate(self, value):
        if len(value) not in (3, 6):
            raise InvalidValue, _("Color length must be 3 or 6 characters")
        for v in value:
            if v not in string.hexdigits:
                raise InvalidValue, _("Color value must contain only valid color codes (numbers or letters between 'A' end 'F')")
        super(ColorField, self)._validate(value)

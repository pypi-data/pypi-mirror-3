### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces
from zope.component.interfaces import IObjectEvent

# import local interfaces

# import Zope3 packages
from zope.interface import Interface

# import local packages


class INewSiteManagerEvent(IObjectEvent):
    """Event interface for new site manager event"""


#
# Generic list interface
#

class IListInfo(Interface):
    """Custom interface used to handle list-like components"""

    def count():
        """Get list items count"""

    def index():
        """Get position of the given item"""

    def __contains__():
        """Check if given value is int list"""

    def __getitem__():
        """Return item at given position"""

    def __iter__():
        """Iterator over list items"""


class IListWriter(Interface):
    """Writer interface for list-like components"""

    def append():
        """Append value to list"""

    def extend():
        """Extend list with given items"""

    def insert():
        """Insert item to given index"""

    def pop():
        """Pop item from list and returns it"""

    def remove():
        """Remove given item from list"""

    def reverse():
        """Sort list in reverse order"""

    def sort():
        """Sort list"""


class IList(IListInfo, IListWriter):
    """Marker interface for list-like components"""


#
# Generic dict interface
#

class IDictInfo(Interface):
    """Custom interface used to handle dict-like components"""

    def keys():
        """Get list of keys for the dict"""

    def has_key(key):
        """Check to know if dict includes the given key"""

    def get(key, default=None):
        """Get given key or default from dict"""

    def copy():
        """Duplicate content of dict"""

    def __contains__(key):
        """Check if given key is in dict"""

    def __getitem__(key):
        """Get given key value from dict"""

    def __iter__():
        """Iterator over dictionnary keys"""


class IDictWriter(Interface):
    """Writer interface for dict-like components"""

    def clear():
        """Clear dict"""

    def update(b):
        """Update dict with given values"""

    def setdefault(key, failobj=None):
        """Create value for given key if missing"""

    def pop(key, *args):
        """Remove and return given key from dict"""

    def popitem():
        """Pop item from dict"""

    def __setitem__(key, value):
        """Update given key with given value"""

    def __delitem__(key):
        """Remove selected key from dict"""


class IDict(IDictInfo, IDictWriter):
    """Marker interface for dict-like components"""

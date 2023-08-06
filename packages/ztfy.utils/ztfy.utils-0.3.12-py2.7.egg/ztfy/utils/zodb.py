### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2012 Thierry Florac <tflorac AT ulthar.net>
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
from persistent.interfaces import IPersistent
from transaction.interfaces import ITransactionManager
from ZODB.interfaces import IConnection

# import local interfaces

# import Zope3 packages
from zope.component import adapter
from zope.interface import implementer

# import local packages


# IPersistent adapters copied from zc.twist package
# also register this for adapting from IConnection
@adapter(IPersistent)
@implementer(ITransactionManager)
def transactionManager(obj):
    conn = IConnection(obj) # typically this will be
                            # zope.app.keyreference.persistent.connectionOfPersistent
    try:
        return conn.transaction_manager
    except AttributeError:
        return conn._txn_mgr
        # or else we give up; who knows.  transaction_manager is the more
        # recent spelling.

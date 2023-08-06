##############################################################################
#
# Copyright (c) 2005-2009 Zope Foundation and Contributors.
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
"""Query interfaces

$Id: interfaces.py 114321 2010-07-08 08:33:43Z janwijbrand $
"""

from zope.interface import Interface

class IQuery(Interface):

    def searchResults(
        query, context=None, sort_field=None, limit=None, reverse=False):

        """Query indexes.

        The query argument is a query composed of terms. Optionally provide
        the `context` parameter for the component lookups.

        Optionally provide a `sort_field` tuple that determines the index used
        to sort the result set with. This index is required to provide
        IIndexSort.

        Optionally provide a `limit` parameter to limit the result set to the
        given size.

        Optionally provide a `reverse` parameter to reverse the order of the
        result set.

        """

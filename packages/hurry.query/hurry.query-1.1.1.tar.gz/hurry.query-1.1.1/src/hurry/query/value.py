##############################################################################
#
# Copyright (c) 2005-2008 Zope Foundation and Contributors.
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
"""Query terms for zc.catalog's ValueIndex

$Id: value.py 112992 2010-06-03 08:22:48Z janwijbrand $
"""
from zc.catalog.interfaces import IValueIndex

from hurry.query import query


class ValueTerm(query.IndexTerm):

    def getIndex(self, context):
        index = super(ValueTerm, self).getIndex(context)
        assert IValueIndex.providedBy(index)
        return index


class Eq(ValueTerm):

    def __init__(self, index_id, value):
        assert value is not None
        super(Eq, self).__init__(index_id)
        self.value = value

    def apply(self, context=None):
        return self.getIndex(context).apply({'any_of': (self.value,)})


class NotEq(ValueTerm):

    def __init__(self, index_id, not_value):
        super(NotEq, self).__init__(index_id)
        self.not_value = not_value

    def apply(self, context=None):
        index = self.getIndex(context)
        values = list(index.values())
        # the remove method produces a value error when the value to
        # be removed is not in the list in the first place.  Having a
        # try/except clause is more efficent than first searching the
        # list for the value to remove.
        try:
            values.remove(self.not_value)
        except ValueError:
            pass
        return index.apply({'any_of': values})


class Between(ValueTerm):

    def __init__(self, index_id, min_value=None, max_value=None,
                 exclude_min=False, exclude_max=False):
        super(Between, self).__init__(index_id)
        self.min_value = min_value
        self.max_value = max_value
        self.exclude_min = exclude_min
        self.exclude_max = exclude_max

    def apply(self, context=None):
        return self.getIndex(context).apply(
            {'between': (self.min_value, self.max_value,
                         self.exclude_min, self.exclude_max)})


class Ge(Between):

    def __init__(self, index_id, min_value):
        super(Ge, self).__init__(index_id, min_value=min_value)


class Le(Between):

    def __init__(self, index_id, max_value):
        super(Le, self).__init__(index_id, max_value=max_value)


class In(ValueTerm):

    def __init__(self, index_id, values):
        assert None not in values
        super(In, self).__init__(index_id)
        self.values = values

    def apply(self, context=None):
        return self.getIndex(context).apply({'any_of': self.values})


class ExtentAny(ValueTerm):
    """Any ids in the extent that are indexed by this index."""

    def __init__(self, index_id, extent):
        super(ExtentAny, self).__init__(index_id)
        self.extent = extent

    def apply(self, context=None):
        return self.getIndex(context).apply({'any': self.extent})


class ExtentNone(ValueTerm):
    """Any ids in the extent that are not indexed by this index."""

    def __init__(self, index_id, extent):
        super(ExtentNone, self).__init__(index_id)
        self.extent = extent

    def apply(self, context=None):
        return self.getIndex(context).apply({'none': self.extent})

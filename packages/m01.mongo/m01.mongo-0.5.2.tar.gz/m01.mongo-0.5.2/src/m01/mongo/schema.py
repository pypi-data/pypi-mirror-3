###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import re
import datetime
import zope.interface
import zope.schema._field
import zope.schema.interfaces

from m01.mongo import interfaces
import m01.mongo.util


class MongoList(zope.schema._field.AbstractCollection):
    """A field representing a List, internaly using a traversable container."""

    zope.interface.implements(interfaces.IMongoList)

    _type = (m01.mongo.util.MongoItemsData, m01.mongo.util.MongoListData, list)

    def __init__(self, value_type=None, unique=False, **kw):
        # whine if value_type is not defined because we need it for identify
        # the list data types e.g. MongoItems or MongoListData
        if value_type is None:
            raise ValueError("Missing 'value_type' in field")
        super(MongoList, self).__init__(value_type, unique, **kw)

    def set(self, obj, value):
        super(MongoList, self).set(obj, value)
        try:
            # locate the given item, but note, this set method is bypassed if we
            # use MongoFieldProperty which stores the value in __dict__
            value.__parent__ = obj
            value.__name__ = self.__name__
        except AttributeError, e:
            pass


class MongoDate(zope.schema._field.Date):
    """A field representing a date, internaly using an ordinal integer value."""

    zope.interface.implements(interfaces.IMongoDate)

    _type = (int, datetime.date)

    def set(self, obj, value):
        if isinstance(value, int):
            value = datetime.date.fromordinal(value)
        super(MongoDate, self).set(obj, value)


# zope.schema string based fields using unicode
_isuri = re.compile(
    # scheme
    r"[a-zA-z0-9+.-]+:"
    # non space (should be pickier)
    r"\S*$").match

class URI(zope.schema.TextLine):
    """URI schema field using unicode as stored value"""

    zope.interface.implements(zope.schema.interfaces.IURI)

    _type = unicode

    def _validate(self, value):
        super(URI, self)._validate(value)
        if _isuri(value):
            return
        raise zope.schema.interfaces.InvalidURI(value)

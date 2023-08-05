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

import datetime
import zope.schema
import m01.mongo.schema
import m01.mongo.util
import m01.mongo.tm

_marker = object()

from m01.mongo import LOCAL


class MongoFieldProperty(object):
    """Computed attributes based on schema fields

    Mongo field property provide default values, data validation and error
    messages based on data found in field meta-data.

    Note that MongoFieldProperty cannot be used with slots. They can only
    be used for attributes stored in instance dictionaries.

    Use this field property for any kind of values except for store MongoObject
    as values on persistent zope objects.

    """

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__
        self.__field = field
        self.__name = name
        self.__type = field._type
        # preconditions
        if isinstance(field, zope.schema.Date):
            raise TypeError(
                "Use MongoDateProperty for Date field %s" % self.__name)
        if isinstance(field, (zope.schema.List, zope.schema.Tuple)):
            raise TypeError(
                "Use MongoList for List or Tuple field %s" % self.__name)
        # setup data factory
        if isinstance(field, m01.mongo.schema.MongoList):
            if isinstance(field.value_type, zope.schema.Object):
                self.__data = m01.mongo.util.MongoItemsData
            else:
                self.__data = m01.mongo.util.MongoListData

    def __get__(self, inst, klass):
        if inst is None:
            return self
        value = inst.__dict__.get(self.__name, _marker)
        if value is _marker:
            field = self.__field.bind(inst)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self.__name)
        if isinstance(value, (tuple, list)):
            # we could get a default value which is an empty list. If so,
            # replace the empty default list value with our item data storage
            # which we setup in our __init_ method.
            value = self.__data(value)
            value.__parent__ = inst
            value.__name__ = self.__name
            inst.__dict__[self.__name] = value
        # take care with this value, it could be a global referenced schema
        # default value. See m01.mongo.util.MongoListData.__init__ for info
        return value

    def __set__(self, inst, value):
        # first locate our value if there is a __parent__ attr
        if hasattr(value, '__parent__'):
            value.__parent__ = inst
        if isinstance(value, (tuple, list)):
            # convert list values. Take care, the value could be a global
            # referenced schema default value. But our __data list can handle
            # that.
            value = self.__data(value)
            value.__parent__ = inst
            value.__name__ = self.__name
        elif self.__type == str and value is not None:
            # we get a unicode value from MongoDB, convert the value to str
            value = self.__type(value)
        # now validate
        field = self.__field.bind(inst)
        field.validate(value)
        if field.readonly and inst.__dict__.has_key(self.__name):
            raise ValueError(self.__name, 'field is readonly')
        inst.__dict__[self.__name] = value
        # mark as changed
        inst._m_changed = True

    def __delete__(self, inst):
        value = inst.__dict__.get(self.__name, _marker)
        if value is not _marker:
            del inst.__dict__[self.__name]
            inst._m_changed = True

    def __getattr__(self, name):
        return getattr(self.__field, name)


class MongoDateProperty(object):
    """Computed attributes based on schema fields

    Mongo field property which will convert a given Date to ordinal and back.
    
    Note, we need to do this beacuse BSON and pymongo do not support date
    objects. There is also a restriction in datetime conversion.
    
    Note: we need to do this because pymongo uses calendar.timegm() and
    datetime.utcfromtimestamp for datetime object. This won't work for 
    datetime object outside 1970 - 2038.
    """

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__
        self.__field = field
        self.__name = name
        if not isinstance(field, m01.mongo.schema.MongoDate):
            raise TypeError(
                "Only use MongoDateProperty for MongoDate field")

    def __get__(self, inst, klass):
        # ordinal to date conversion
        if inst is None:
            return self
        value = inst.__dict__.get(self.__name, _marker)
        if value is _marker:
            field = self.__field.bind(inst)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self.__name)
        # convert to date
        if value is not None:
            return datetime.date.fromordinal(value)
        return value

    def __set__(self, inst, value):
        # date to ordinal conversion
        if isinstance(value, int):
            value = datetime.date.fromordinal(value)
        field = self.__field.bind(inst)
        field.validate(value)
        if field.readonly and inst.__dict__.has_key(self.__name):
            raise ValueError(self.__name, 'field is readonly')
        inst.__dict__[self.__name] = value.toordinal()
        inst._m_changed = True

    def __delete__(self, inst):
        value = inst.__dict__.get(self.__name, _marker)
        if value is not _marker:
            del inst.__dict__[self.__name]
            inst._m_changed = True

    def __getattr__(self, name):
        return getattr(self.__field, name)


class MongoGeoLocationProperty(object):
    """Computed GeoLocation based on given data"""

    def __init__(self, field, name=None, geoLocationFactory=None):
        if name is None:
            name = field.__name__
        self.__field = field
        self.__name = name
        self.__type = field._type
        if geoLocationFactory is None:
            # prevent recursive import
            from m01.mongo.geo import GeoLocation
            geoLocationFactory = GeoLocation
        self.__factory = geoLocationFactory
        # preconditions
        if not isinstance(field, zope.schema.Object):
            raise TypeError(
                "Use zope.schema.Object for GeoLocation field %s" % self.__name)

    def __get__(self, inst, klass):
        if inst is None:
            return self
        value = inst.__dict__.get(self.__name, _marker)
        if value is _marker:
            field = self.__field.bind(inst)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self.__name)
        return value

    def __set__(self, inst, value):
        # allowed values are a dict with {'lon', <lon>, 'lat': <lat>} or an 
        # IGeoLocation instance or even a list with lon, lat values
        if isinstance(value, (dict, list)):
            # convert dict data
            value = self.__factory(value)
        if value is not None:
            # locate them
            value.__parent__ = inst
            value.__name__ = self.__name
        # now validate
        field = self.__field.bind(inst)
        field.validate(value)
        if field.readonly and inst.__dict__.has_key(self.__name):
            raise ValueError(self.__name, 'field is readonly')
        inst.__dict__[self.__name] = value
        # mark as changed
        inst._m_changed = True

    def __delete__(self, inst):
        value = inst.__dict__.get(self.__name, _marker)
        if value is not _marker:
            del inst.__dict__[self.__name]
            inst._m_changed = True

    def __getattr__(self, name):
        return getattr(self.__field, name)


# TODO: change property setup method, allow to define more then one
# factories. Use the factories based on the _type if we create a MongoObject
# Also allow to define an explicit getCollection method
class MongoObjectProperty(object):
    """Computed MongoObject based on schema fields and given configuration
    using an unique _moid attribute as __parent__ reference and an attribute
    name for build a unique _oid.

    MongoObjectProperty provides default values, data validation and error
    messages based on data found in field meta-data.

    The MongoItemProperty can read and write a MongoObject from and to MongoDB.
    The access to the MongoDB is lazy which means the object get only loaded if
    we access them. A transaction data manager is used for write data back to
    the MongoDB on transaction commit.
    
    Use this field property only for store MongoObject objects as attribute
    values. Use the default MongoFieldProperty and MongoSubItem objects if you
    like to store objects as list or dict items.

    This property is used if you need to set a MongoObject as an attribute
    on an object. Such MongoObject attributes get stored in a MongoDB
    collection defined by the getCollection method.

    This property can get used on persistent zope object or on non persistent
    MongoItem based objects. If you use a MongoObjectProperty in a MongoItem,
    you don't have to setup or dump such MongoObject attribute values. They
    are full independent from their MongoAwareObject.

    MongoObject provide everything a normal MongoItem can provide. Which means
    you can use MongoSubItem, converters, etc.

    """

    def __init__(self, field, factory, getCollection=None):
        self.__factory = factory
        if getCollection is None:
            self.__getCollection = factory.getCollection
        else:
            self.__getCollection = getCollection
        self.__field = field
        self.__name = field.__name__
        if not isinstance(field, zope.schema.Object):
            raise TypeError(
                "Can only use MongoObjectProperty for zope.schema.Object field")

    def getMongoObject(self, inst):
        _oid = u'%s:%s' % (inst._moid, self.__name)
        value = LOCAL.__dict__.get(_oid, _marker)
        if value is _marker:
            collection = self.__getCollection(inst)
            data = collection.find_one({'_oid':_oid})
            if data is not None and not data.get('removed'):
                data['__parent__'] = inst
                assert data['__name__'] == self.__name
                value = self.__factory(data)
                # cache mongo object
                LOCAL.__dict__[_oid] = value
                # setup transaction handling
                m01.mongo.tm.ensureMongoTransaction(value)
        elif value.removed:
            value = _marker
        return value

    def __get__(self, inst, klass):
        if inst is None:
            return self
        value = self.getMongoObject(inst)
        if value is _marker:
            # find default value
            field = self.__field.bind(inst)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self.__name)
        return value

    def __set__(self, inst, value):
        # Note, we do not need to remove existing items, they get overriden
        # with the new one because a new MongoObject provides the same _oid.
        if not hasattr(inst, '_moid'):
            raise ValueError("MongoObject __parent__ doens't provide an _moid")

        # remove old item
        old = self.getMongoObject(inst)
        if old is not _marker:
            # mark as removed and _m_changed which forces that the object get
            # removed in voteCommit call
            old.removed = True
            # setup transaction and append the old MongoObject before we add
            # a new one. This will ensure that we remove the item from MongoDB
            # before we add the new one. Note: both use the same _oid
            m01.mongo.tm.ensureMongoTransaction(value)
        if value is None:
            # bind and validate, the above code marks an old object as removed
            # if there was any
            field = self.__field.bind(inst)
            field.validate(value)
            return

        # set or compare __parent__ which is required for _oid
        if value.__parent__ is None:
            value.__parent__ = inst
        elif value.__parent__ is not inst:
            raise ValueError(
                "Wrong __parent__ given, __parent__ must be %r" % inst,
                value.__parent__)

        # set or compare __name__ which is required for _oid
        if value.__name__ is None:
            value.__name__ = unicode(self.__name)
        elif value.__name__ != self.__name:
            raise ValueError(
                "Wrong __name__ given, __name__ must be %r" % self.__name,
                value.__name__)

        # now we can get and approve the _oid
        _oid = u'%s:%s' % (inst._moid, self.__name)
        if _oid != value._oid:
            raise ValueError("MongoObject _oid %r does not compare", value._oid)
        # mark as changed
        value._m_changed = True

        # bind and validate
        field = self.__field.bind(inst)
        field.validate(value)
        # validate readonly
        if field.readonly and self.__getCollection(inst).find_one(
            {'_oid': value._oid}.count()):
            raise ValueError(self.__name, 'field is readonly')
        # setup transaction and append the MongoObject
        m01.mongo.tm.ensureMongoTransaction(value)
        # cache mongo object
        LOCAL.__dict__[_oid] = value

    def __delete__(self, inst):
        # this clever concept will force that the MongoObject get removed on
        # transaction commit
        value = self.getMongoObject(inst)
        if value is not _marker:
            # mark as removed and _m_changed which forces that the object get
            # removed in voteCommit call
            value.removed = True

    def __getattr__(self, name):
        return getattr(self.__field, name)

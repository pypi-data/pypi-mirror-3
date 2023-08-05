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

import time
import datetime
import struct
import threading
import zope.component

import pymongo.objectid

from m01.mongo import interfaces

LOCAL = threading.local()


# UTC support
ZERO = datetime.timedelta(0)


class FixedOffsetBase(datetime.tzinfo):
    """Fixed offset base class."""

    def __init__(self, offset, name):
        if isinstance(offset, int):
            offset = datetime.timedelta(minutes=offset)
        self.__offset = offset
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO

    def __repr__(self):
        return self.__name


class FixedOffset(FixedOffsetBase):
    """Pickable implementation of fixed offset used for deepcopy."""

    def __init__(self, offset=None, name=None):
        FixedOffsetBase.__init__(self, offset, name)

# Fixed offset timezone representing UTC
UTC = FixedOffset(0, "UTC")


# connection
def getMongoDBConnection(name):
    """Returns a mongodb connection"""
    pool = zope.component.getUtility(interfaces.IMongoConnectionPool,
        name=name)
    return pool.connection


def clearThreadLocalCache(event=None):
    """A subscriber to EndRequestEvent

    Cleans up the thread local cache on each end request.
    """
    for key in LOCAL.__dict__.keys():
        del LOCAL.__dict__[key]


def getObjectId(counter=0):
    """Knows how to generate similar ObjectId based on integer (counter)
    
    Note: this method can get used if you need to define similar ObjectId
    in a non persistent environment if need to bootstrap mongo containers.
    """
    # not every system can generate timestamps from 0 (zero) seconds
    secs = 60*60
    secs += counter
    time_tuple = time.gmtime(secs)
    ts = time.mktime(time_tuple)
    oid = struct.pack(">i", int(ts)) + "\x00" * 8
    return pymongo.objectid.ObjectId(oid)


def getObjectIdByTimeStr(tStr, format="%Y-%m-%d %H:%M:%S"):
    """Knows how to generate similar ObjectId based on a time string
    
    The time string format used by default is ``%Y-%m-%d %H:%M:%S``.
    Use the current development time which could prevent duplicated
    ObjectId. At least some kind of ;-)
    """
    time.strptime(tStr, "%Y-%m-%d %H:%M:%S")
    ts = time.mktime(tStr)
    oid = struct.pack(">i", int(ts)) + "\x00" * 8
    return pymongo.objectid.ObjectId(oid)

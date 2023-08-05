======
README
======

IMPORTANT:
If you run the tests with the --all option a real mongodb stub server will
start at port 45017!

This package provides non persistent MongoDB object implementations. They can
simply get mixed with persistent.Persistent and contained.Contained if you like
to use them in a mixed MongoDB/ZODB application setup. We currently use this
framework as ORM (object relation mapper) where we map MongoDB objects
to python/zope schema based objects including validation etc.

In our last project, we started with a mixed ZODB/MongoDB application where we
mixed persistent.persistent into IMongoContainer objects. But later we where
so exited about the performance and stability that we removed the ZODB
persistence layer at all. Now we use a ZODB less setup in our application
where we start with a non persistent item as our application root. All required
tools where we use for such a ZODB less application setup are located in the
m01.publisher and p01.recipe.setup package.

NOTE: Some of this test use a fake mongodb located in m01/mongo/testing and some
other tests will use our mongdb stub from the m01.stub package. You can run
the tests with the --all option if you like to run the full tests which will
start and stop the mongodb stub server.

NOTE:
All mongo item interfaces will not provide ILocation or IContained but the
bass mongo item implementations will implement Location which provides the
ILocation interface directly. This makes it simpler for permission
declaration in ZCML.


Testing
-------

  >>> import pprint
  >>> import zope.component
  >>> from m01.mongo import interfaces
  >>> from m01.mongo import getMongoDBConnection
  >>> from m01.mongo.pool import MongoConnectionPool


MongoConnectionPool
--------------------

We need to setup a mongo connection pool. We can do this with a global utility
configuration. Note we use a different port with our stub server setup:

  >>> mongoConnectionPool = MongoConnectionPool('localhost', 45020)
  >>> zope.component.provideUtility(mongoConnectionPool,
  ...     interfaces.IMongoConnectionPool, name='m01.mongo.testing')

The connection pool stores the connection in threading local.


Mongo Connection
----------------

Now we are able to get a connection pool:

  >>> pool = zope.component.getUtility(interfaces.IMongoConnectionPool,
  ...    name='m01.mongo.testing')

Such a pool knows the connection which is observed by thread local:

  >>> conn1 = pool.connection
  >>> conn1
  Connection('localhost', 45020)

We can also use the getMongoDBConnection which knows how to get a connection:

  >>> conn = getMongoDBConnection('m01.mongo.testing')
  >>> conn
  Connection('localhost', 45020)

As you can see the connection is able to access the database:

  >>> db = conn.m01MongoTesting
  >>> db
  Database(Connection('localhost', 45020), u'm01MongoTesting')

A data base can retrun a collection:

  >>> collection = db['m01MongoTest']
  >>> collection
  Collection(Database(Connection('localhost', 45020), u'm01MongoTesting'), u'm01MongoTest')

As you can see we can write to the collection:

  >>> collection.update({'_id': '123'}, {'$inc': {'counter': 1}}, upsert=True)

And we can read from the collection:

  >>> collection.find_one({'_id': '123'})
  {u'_id': u'123', u'counter': 1}

Remove the result from our test collection:

  >>> collection.remove({'_id': '123'})

Now tear down our MongoDB database with our current MongoDB connection:

  >>> conn.drop_database('m01MongoTesting')


__version__ = '1.0'
__author__ = 'Juan Batiz-Benet <juan@benet.ai>'
__doc__ = '''
aws datastore implementation.

Tested with:
* boto 2.1.1

'''

#TODO: Implement queries using a key index.
#TODO: Implement TTL (and key configurations)


import datastore


class S3BucketDatastore(datastore.Datastore):
  '''Simple aws s3 datastore. Does not support queries.

  The s3 interface is very similar to datastore's. The only differences are:
  - values must be strings (SerializerShimDatastore)
  - keys must be converted into strings
  '''

  def __init__(self, s3bucket, serializer=None):
    '''Initialize the datastore with given s3 connection `redis`.

    Args:
      s3bucket: An s3 bucket to use.

    Example::

      from boto.s3.connection import S3Connection
      s3conn = S3Connection('<aws access key>', '<aws secret key>')
      bucket =
    '''
    self._s3bucket = s3bucket

    # use a SerializerShimDatastore to ensure values are stringified
    serial = datastore.SerializerShimDatastore(mapper, serializer=serializer)

    # initialize ShimDatastore with serial as our child_datastore
    super(RedisDatastore, self).__init__(serial)

  def query(self, query):
    '''Returns an iterable of objects matching criteria expressed in `query`

    Args:
      query: Query object describing the objects to return.

    Raturns:
      Cursor with all objects matching criteria
    '''
    #TODO
    raise NotImplementedError


'''
Hello World:

    >>> import redis
    >>> import datastore
    >>> from datastore.impl.redis import RedisDatastore
    >>> r = redis.Redis()
    >>> ds = RedisDatastore(r)
    >>>
    >>> hello = datastore.Key('hello')
    >>> ds.put(hello, 'world')
    >>> ds.contains(hello)
    True
    >>> ds.get(hello)
    'world'
    >>> ds.delete(hello)
    >>> ds.get(hello)
    None

'''

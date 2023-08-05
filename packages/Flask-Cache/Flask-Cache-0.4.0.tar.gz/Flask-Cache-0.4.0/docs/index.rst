Flask-Cache
================

.. module:: flaskext.cache

Installation
------------

Install the extension with one of the following commands::

    $ easy_install Flask-Cache

or alternatively if you have pip installed::

    $ pip install Flask-Cache


Configuring Flask-Cache
-----------------------

The following configuration values exist for Flask-Cache:

.. tabularcolumns:: |p{6.5cm}|p{8.5cm}|

=============================== =========================================
``CACHE_TYPE``                  Specifies which type of caching object to
                                use. This is an import string that will
                                be imported and instantiated. It is
                                assumed that the import object is a
                                function that will return a cache
                                object that adheres to the werkzeug cache 
                                API.
                                
                                For werkzeug.contrib.cache objects, you
                                do not need to specify the entire 
                                import string, just one of the following
                                names.
                                
                                Built-in cache types:
                                
                                * **null**: NullCache
                                * **simple**: SimpleCache
                                * **memcached**: MemcachedCache
                                * **gaememcached**: GAEMemcachedCache
                                * **redis**: RedisCache (Werkzeug 0.7 required)
                                * **filesystem**: FileSystemCache
                                
``CACHE_ARGS``                  Optional list to unpack and pass during
                                the cache class instantiation.
``CACHE_OPTIONS``               Optional dictionary to pass during the
                                cache class instantiation.
``CACHE_DEFAULT_TIMEOUT``       The default timeout that is used if no
                                timeout is specified. Unit of time is
                                seconds.
``CACHE_THRESHOLD``             The maximum number of items the cache
                                will store before it starts deleting
                                some. Used only for SimpleCache and
                                FileSystemCache
``CACHE_KEY_PREFIX``            A prefix that is added before all keys.
                                This makes it possible to use the same
                                memcached server for different apps.
                                Used only for MemcachedCache and
                                GAEMemcachedCache.
``CACHE_MEMCACHED_SERVERS``     A list or a tuple of server addresses.
                                Used only for MemcachedCache
``CACHE_REDIS_HOST``            A Redis server host. Used only for RedisCache.
``CACHE_REDIS_PORT``            A Redis server port. Default is 6379.
                                Used only for RedisCache.
``CACHE_DIR``                   Directory to store cache. Used only for
                                FileSystemCache.
=============================== =========================================

In addition the standard Flask ``TESTING`` configuration option is used. If this
is True then **Flask-Cache** will use NullCache only.

Set Up
------

Cache is managed through a ``Cache`` instance::

    from flask import Flask
    from flaskext.cache import Cache

    app = Flask(__name__)
    cache = Cache(app)

You may also set up your ``Cache`` instance later at configuration time using
**init_app** method::

    cache = Cache()

    app = Flask(__name__)
    cache.init_app(app)

Caching View Functions
----------------------

To cache view functions you will use the :meth:`~Cache.cached` decorator.
This decorator will use request.path by default for the cache_key.::

    @cache.cached(timeout=50)
    def index():
        return render_template('index.html')

The cached decorator has another optional argument called ``unless``. This
argument accepts a callable that returns True or False. If ``unless`` returns
``True`` then it will bypass the caching mechanism entirely.

Caching Other Functions
-----------------------

Using the same ``@cached`` decorator you are able to cache the result of other
non-view related functions. The only stipulation is that you replace the
``key_prefix``, otherwise it will use the request.path cache_key.::

    @cache.cached(timeout=50, key_prefix='all_comments')
    def get_all_comments():
        comments = do_serious_dbio()
        return [x.author for x in comments]

    cached_comments = get_all_comments()

Memoization
-----------

See :meth:`~Cache.memoize`

In memoization, the functions arguments are also included into the cache_key.

.. note::

	With functions that do not receive arguments, :meth:`~Cache.cached` and
	:meth:`~Cache.memoize` are effectively the same.
	
Memoize is also designed for instance objects, since it will take into account
that functions id. The theory here is that if you have a function you need
to call several times in one request, it would only be calculated the first
time that function is called with those arguments. For example, an sqlalchemy
object that determines if a user has a role. You might need to call this 
function many times during a single request.::

	User(db.Model):
		@cache.memoize(50)
		def has_membership(role):
			return self.groups.filter_by(role=role).count() >= 1
			
		
Deleting memoize cache
``````````````````````

.. versionadded:: 0.2

You might need to delete the cache on a per-function bases. Using the above
example, lets say you change the users permissions and assign them to a role,
but now you need to re-calculate if they have certain memberships or not.
You can do this with the :meth:`~Cache.delete_memoized` function.::

	cache.delete_memoized('has_membership')
	
.. note::

  If only the function name is given as parameter, all the memoized versions
  of it will be erazed. However, you can delete specific cache by providing the
  same parameter values as when caching. In following example only the ``user``
  -roled cache is erased:

  .. code-block:: python

     has_membership('admin')
     has_membership('user')

     cache.delete_memoized('has_membership', 'user')


Custom Cache Backends
---------------------

You are able to easily add your own custom cache backends by exposing a function
that can instantiate and return a cache object. ``CACHE_TYPE`` will be the
import string to your custom function. It should expect to receive three
arguments.

* ``app``
* ``args``
* ``kwargs``

Your custom cache object must also subclass the 
:class:`werkzeug.contrib.cache.BaseCache` class. Flask-Cache will make sure
that ``threshold`` is already included in the kwargs options dictionary since
it is common to all BaseCache classes.

An example Redis cache implementation::

	#: the_app/custom.py
	class RedisCache(BaseCache):
		def __init__(self, servers, default_timeout=500):
			pass
	
	def redis(app, args, kwargs):
	   args.append(app.config['REDIS_SERVERS'])
	   return RedisCache(*args, **kwargs)

With this example, your ``CACHE_TYPE`` might be ``the_app.custom.redis``

API
---

.. autoclass:: Cache
   :members: get, set, add, delete, cached, memoize, delete_memoized, get_memoize_names, get_memoize_keys

.. include:: ../CHANGES

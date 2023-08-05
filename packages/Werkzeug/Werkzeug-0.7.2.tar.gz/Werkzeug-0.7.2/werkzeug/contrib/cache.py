# -*- coding: utf-8 -*-
"""
    werkzeug.contrib.cache
    ~~~~~~~~~~~~~~~~~~~~~~

    The main problem with dynamic Web sites is, well, they're dynamic.  Each
    time a user requests a page, the webserver executes a lot of code, queries
    the database, renders templates until the visitor gets the page he sees.

    This is a lot more expensive than just loading a file from the file system
    and sending it to the visitor.

    For most Web applications, this overhead isn't a big deal but once it
    becomes, you will be glad to have a cache system in place.

    How Caching Works
    =================

    Caching is pretty simple.  Basically you have a cache object lurking around
    somewhere that is connected to a remote cache or the file system or
    something else.  When the request comes in you check if the current page
    is already in the cache and if so, you're returning it from the cache.
    Otherwise you generate the page and put it into the cache. (Or a fragment
    of the page, you don't have to cache the full thing)

    Here is a simple example of how to cache a sidebar for a template::

        def get_sidebar(user):
            identifier = 'sidebar_for/user%d' % user.id
            value = cache.get(identifier)
            if value is not None:
                return value
            value = generate_sidebar_for(user=user)
            cache.set(identifier, value, timeout=60 * 5)
            return value

    Creating a Cache Object
    =======================

    To create a cache object you just import the cache system of your choice
    from the cache module and instantiate it.  Then you can start working
    with that object:

    >>> from werkzeug.contrib.cache import SimpleCache
    >>> c = SimpleCache()
    >>> c.set("foo", "value")
    >>> c.get("foo")
    'value'
    >>> c.get("missing") is None
    True

    Please keep in mind that you have to create the cache and put it somewhere
    you have access to it (either as a module global you can import or you just
    put it into your WSGI application).

    :copyright: (c) 2011 by the Werkzeug Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
import os
import re
import tempfile
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5
from itertools import izip
from time import time
from cPickle import loads, dumps, load, dump, HIGHEST_PROTOCOL
from werkzeug.posixemulation import rename

def _items(mappingorseq):
    """Wrapper for efficient iteration over mappings represented by dicts
    or sequences::

        >>> for k, v in _items((i, i*i) for i in xrange(5)):
        ...    assert k*k == v

        >>> for k, v in _items(dict((i, i*i) for i in xrange(5))):
        ...    assert k*k == v

    """
    return mappingorseq.iteritems() if hasattr(mappingorseq, 'iteritems') \
        else mappingorseq

class BaseCache(object):
    """Baseclass for the cache systems.  All the cache systems implement this
    API or a superset of it.

    :param default_timeout: the default timeout that is used if no timeout is
                            specified on :meth:`set`.
    """

    def __init__(self, default_timeout=300):
        self.default_timeout = default_timeout

    def get(self, key):
        """Looks up key in the cache and returns the value for it.
        If the key does not exist `None` is returned instead.

        :param key: the key to be looked up.
        """
        return None

    def delete(self, key):
        """Deletes `key` from the cache.  If it does not exist in the cache
        nothing happens.

        :param key: the key to delete.
        """
        pass

    def get_many(self, *keys):
        """Returns a list of values for the given keys.
        For each key a item in the list is created.  Example::

            foo, bar = cache.get_many("foo", "bar")

        If a key can't be looked up `None` is returned for that key
        instead.

        :param keys: The function accepts multiple keys as positional
                     arguments.
        """
        return map(self.get, keys)

    def get_dict(self, *keys):
        """Works like :meth:`get_many` but returns a dict::

            d = cache.get_dict("foo", "bar")
            foo = d["foo"]
            bar = d["bar"]

        :param keys: The function accepts multiple keys as positional
                     arguments.
        """
        return dict(izip(keys, self.get_many(*keys)))

    def set(self, key, value, timeout=None):
        """Adds a new key/value to the cache (overwrites value, if key already
        exists in the cache).

        :param key: the key to set
        :param value: the value for the key
        :param timeout: the cache timeout for the key (if not specified,
                        it uses the default timeout).
        """
        pass

    def add(self, key, value, timeout=None):
        """Works like :meth:`set` but does not overwrite the values of already
        existing keys.

        :param key: the key to set
        :param value: the value for the key
        :param timeout: the cache timeout for the key or the default
                        timeout if not specified.
        """
        pass

    def set_many(self, mapping, timeout=None):
        """Sets multiple keys and values from a mapping.

        :param mapping: a mapping with the keys/values to set.
        :param timeout: the cache timeout for the key (if not specified,
                        it uses the default timeout).
        """
        for key, value in _items(mapping):
            self.set(key, value, timeout)

    def delete_many(self, *keys):
        """Deletes multiple keys at once.

        :param keys: The function accepts multiple keys as positional
                     arguments.
        """
        for key in keys:
            self.delete(key)

    def clear(self):
        """Clears the cache.  Keep in mind that not all caches support
        completely clearing the cache.
        """
        pass

    def inc(self, key, delta=1):
        """Increments the value of a key by `delta`.  If the key does
        not yet exist it is initialized with `delta`.

        For supporting caches this is an atomic operation.

        :param key: the key to increment.
        :param delta: the delta to add.
        """
        self.set(key, (self.get(key) or 0) + delta)

    def dec(self, key, delta=1):
        """Decrements the value of a key by `delta`.  If the key does
        not yet exist it is initialized with `-delta`.

        For supporting caches this is an atomic operation.

        :param key: the key to increment.
        :param delta: the delta to subtract.
        """
        self.set(key, (self.get(key) or 0) - delta)


class NullCache(BaseCache):
    """A cache that doesn't cache.  This can be useful for unit testing.

    :param default_timeout: a dummy parameter that is ignored but exists
                            for API compatibility with other caches.
    """


class SimpleCache(BaseCache):
    """Simple memory cache for single process environments.  This class exists
    mainly for the development server and is not 100% thread safe.  It tries
    to use as many atomic operations as possible and no locks for simplicity
    but it could happen under heavy load that keys are added multiple times.

    :param threshold: the maximum number of items the cache stores before
                      it starts deleting some.
    :param default_timeout: the default timeout that is used if no timeout is
                            specified on :meth:`~BaseCache.set`.
    """

    def __init__(self, threshold=500, default_timeout=300):
        BaseCache.__init__(self, default_timeout)
        self._cache = {}
        self.clear = self._cache.clear
        self._threshold = threshold

    def _prune(self):
        if len(self._cache) > self._threshold:
            now = time()
            for idx, (key, (expires, _)) in enumerate(self._cache.items()):
                if expires <= now or idx % 3 == 0:
                    self._cache.pop(key, None)

    def get(self, key):
        now = time()
        expires, value = self._cache.get(key, (0, None))
        if expires > time():
            return loads(value)

    def set(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        self._prune()
        self._cache[key] = (time() + timeout, dumps(value, HIGHEST_PROTOCOL))

    def add(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        if len(self._cache) > self._threshold:
            self._prune()
        item = (time() + timeout, dumps(value, HIGHEST_PROTOCOL))
        self._cache.setdefault(key, item)

    def delete(self, key):
        self._cache.pop(key, None)


_test_memcached_key = re.compile(r'[^\x00-\x21\xff]{1,250}$').match

class MemcachedCache(BaseCache):
    """A cache that uses memcached as backend.

    The first argument can either be a list or tuple of server addresses
    in which case Werkzeug tries to import the memcache module and connect
    to it, or an object that resembles the API of a :class:`memcache.Client`.

    Implementation notes:  This cache backend works around some limitations in
    memcached to simplify the interface.  For example unicode keys are encoded
    to utf-8 on the fly.  Methods such as :meth:`~BaseCache.get_dict` return
    the keys in the same format as passed.  Furthermore all get methods
    silently ignore key errors to not cause problems when untrusted user data
    is passed to the get methods which is often the case in web applications.

    :param servers: a list or tuple of server addresses or alternatively
                    a :class:`memcache.Client` or a compatible client.
    :param default_timeout: the default timeout that is used if no timeout is
                            specified on :meth:`~BaseCache.set`.
    :param key_prefix: a prefix that is added before all keys.  This makes it
                       possible to use the same memcached server for different
                       applications.  Keep in mind that
                       :meth:`~BaseCache.clear` will also clear keys with a
                       different prefix.
    """

    def __init__(self, servers, default_timeout=300, key_prefix=None):
        BaseCache.__init__(self, default_timeout)
        if isinstance(servers, (list, tuple)):
            is_cmemcached = is_cmemcache = is_pylibmc = False
            try:
                import cmemcached as memcache
                is_cmemcached = True
            except ImportError:
                try:
                    import cmemcache as memcache
                    is_cmemcache = True
                except ImportError:
                    try:
                        import memcache
                        is_cmemcache = False
                        is_pylibmc = False
                    except ImportError:
                        try:
                            import pylibmc as memcache
                            is_cmemcache = False
                            is_pylibmc = True
                        except ImportError:
                            raise RuntimeError('no memcache module found')

            if is_cmemcache:
                # cmemcache has a bug that debuglog is not defined for the
                # client.  Whenever pickle fails you get a weird
                # AttributeError.
                client = memcache.Client(map(str, servers))
                try:
                    client.debuglog = lambda *a: None
                except Exception:
                    pass
            elif is_pylibmc or is_cmemcached:
                client = memcache.Client(servers, False)
            else:
                client = memcache.Client(servers, False, HIGHEST_PROTOCOL)
        else:
            client = servers

        self._client = client
        self.key_prefix = key_prefix

    def get(self, key):
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if self.key_prefix:
            key = self.key_prefix + key
        # memcached doesn't support keys longer than that.  Because often
        # checks for so long keys can occour because it's tested from user
        # submitted data etc we fail silently for getting.
        if _test_memcached_key(key):
            return self._client.get(key)

    def get_dict(self, *keys):
        key_mapping = {}
        have_encoded_keys = False
        for key in keys:
            if isinstance(key, unicode):
                encoded_key = key.encode('utf-8')
                have_encoded_keys = True
            else:
                encoded_key = key
            if self.key_prefix:
                encoded_key = self.key_prefix + encoded_key
            if _test_memcached_key(key):
                key_mapping[encoded_key] = key
        # the keys call here is important because otherwise cmemcache
        # does ugly things.  What exactly I don't know, I think it does
        # Py_DECREF but quite frankly I don't care.
        d = rv = self._client.get_multi(key_mapping.keys())
        if have_encoded_keys or self.key_prefix:
            rv = {}
            for key, value in d.iteritems():
                rv[key_mapping[key]] = value
        if len(rv) < len(keys):
            for key in keys:
                if key not in rv:
                    rv[key] = None
        return rv

    def add(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if self.key_prefix:
            key = self.key_prefix + key
        self._client.add(key, value, timeout)

    def set(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if self.key_prefix:
            key = self.key_prefix + key
        self._client.set(key, value, timeout)

    def get_many(self, *keys):
        d = self.get_dict(*keys)
        return [d[key] for key in keys]

    def set_many(self, mapping, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        new_mapping = {}
        for key, value in _items(mapping):
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if self.key_prefix:
                key = self.key_prefix + key
            new_mapping[key] = value
        self._client.set_multi(new_mapping, timeout)

    def delete(self, key):
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if self.key_prefix:
            key = self.key_prefix + key
        if _test_memcached_key(key):
            self._client.delete(key)

    def delete_many(self, *keys):
        new_keys = []
        for key in keys:
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if self.key_prefix:
                key = self.key_prefix + key
            if _test_memcached_key(key):
                new_keys.append(key)
        self._client.delete_multi(new_keys)

    def clear(self):
        self._client.flush_all()

    def inc(self, key, delta=1):
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if self.key_prefix:
            key = self.key_prefix + key
        self._client.incr(key, delta)

    def dec(self, key, delta=1):
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if self.key_prefix:
            key = self.key_prefix + key
        self._client.decr(key, delta)


class GAEMemcachedCache(MemcachedCache):
    """Connects to the Google appengine memcached Cache.

    :param default_timeout: the default timeout that is used if no timeout is
                            specified on :meth:`~BaseCache.set`.
    :param key_prefix: a prefix that is added before all keys.  This makes it
                       possible to use the same memcached server for different
                       applications.  Keep in mind that
                       :meth:`~BaseCache.clear` will also clear keys with a
                       different prefix.
    """

    def __init__(self, default_timeout=300, key_prefix=None):
        from google.appengine.api import memcache
        MemcachedCache.__init__(self, memcache.Client(),
                                default_timeout, key_prefix)


class RedisCache(BaseCache):
    """Uses the Redis key-value store as a cache backend.

    The first argument can be either a string denoting address of the Redis
    server or an object resembling an instance of a redis.Redis class.

    Note: Python Redis API already takes care of encoding unicode strings on
    the fly.

    .. versionadded:: 0.7

    :param host: address of the Redis server or an object which API is
                 compatible with the official Python Redis client (redis-py).
    :param port: port number on which Redis server listens for connections
    :param default_timeout: the default timeout that is used if no timeout is
                            specified on :meth:`~BaseCache.set`.

    """
    def __init__(self, host='localhost', port=6379, default_timeout=300):
        BaseCache.__init__(self, default_timeout)
        if isinstance(host, basestring):
            try:
                import redis
            except ImportError:
                raise RuntimeError('no redis module found')
            self._client = redis.Redis(host=host, port=port)
        else:
            self._client = host

    def get(self, key):
        return self._client.get(key)

    def get_many(self, *keys):
        return self._client.mget(keys)

    def set(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        self._client.setex(key, value, timeout)

    def add(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        added = self._client.setnx(key, value)
        if added:
            self._client.expire(key, timeout)

    def set_many(self, mapping, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        pipe = self._client.pipeline()
        for key, value in _items(mapping):
            pipe.setex(key, value, timeout)
        pipe.execute()

    def delete(self, key):
        self._client.delete(key)

    def delete_many(self, *keys):
        self._client.delete(*keys)

    def clear(self):
        self._client.flushdb()

    def inc(self, key, delta=1):
        return self._client.incr(key, delta)

    def dec(self, key, delta=1):
        return self._client.decr(key, delta)


class FileSystemCache(BaseCache):
    """A cache that stores the items on the file system.  This cache depends
    on being the only user of the `cache_dir`.  Make absolutely sure that
    nobody but this cache stores files there or otherwise the cache will
    randomly delete files therein.

    :param cache_dir: the directory where cache files are stored.
    :param threshold: the maximum number of items the cache stores before
                      it starts deleting some.
    :param default_timeout: the default timeout that is used if no timeout is
                            specified on :meth:`~BaseCache.set`.
    :param mode: the file mode wanted for the cache files, default 0600
    """

    #: used for temporary files by the FileSystemCache
    _fs_transaction_suffix = '.__wz_cache'

    def __init__(self, cache_dir, threshold=500, default_timeout=300, mode=0600):
        BaseCache.__init__(self, default_timeout)
        self._path = cache_dir
        self._threshold = threshold
        self._mode = mode
        if not os.path.exists(self._path):
            os.makedirs(self._path)

    def _list_dir(self):
        """return a list of (fully qualified) cache filenames
        """
        return [os.path.join(self._path, fn) for fn in os.listdir(self._path)
                if not fn.endswith(self._fs_transaction_suffix)]

    def _prune(self):
        entries = self._list_dir()
        if len(entries) > self._threshold:
            now = time()
            for idx, fname in enumerate(entries):
                remove = False
                f = None
                try:
                    try:
                        f = open(fname, 'rb')
                        expires = load(f)
                        remove = expires <= now or idx % 3 == 0
                    finally:
                        if f is not None:
                            f.close()
                except Exception:
                    pass
                if remove:
                    try:
                        os.remove(fname)
                    except (IOError, OSError):
                        pass

    def clear(self):
        for fname in self._list_dir():
            try:
                os.remove(fname)
            except (IOError, OSError):
                pass

    def _get_filename(self, key):
        hash = md5(key).hexdigest()
        return os.path.join(self._path, hash)

    def get(self, key):
        filename = self._get_filename(key)
        try:
            f = open(filename, 'rb')
            try:
                if load(f) >= time():
                    return load(f)
            finally:
                f.close()
            os.remove(filename)
        except Exception:
            return None

    def add(self, key, value, timeout=None):
        filename = self._get_filename(key)
        if not os.path.exists(filename):
            self.set(key, value, timeout)

    def set(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        filename = self._get_filename(key)
        self._prune()
        try:
            fd, tmp = tempfile.mkstemp(suffix=self._fs_transaction_suffix,
                                       dir=self._path)
            f = os.fdopen(fd, 'wb')
            try:
                dump(int(time() + timeout), f, 1)
                dump(value, f, HIGHEST_PROTOCOL)
            finally:
                f.close()
            rename(tmp, filename)
            os.chmod(filename, self._mode)
        except (IOError, OSError):
            pass

    def delete(self, key):
        try:
            os.remove(self._get_filename(key))
        except (IOError, OSError):
            pass


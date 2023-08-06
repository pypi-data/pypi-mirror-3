# coding: utf-8

"""
    smooth cache backends
    ~~~~~~~~~~~~~~~~~~~~~
    
    more information in the README.
    
    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import os
import sys
import time

from django.core.cache.backends.filebased import FileBasedCache
from django.core.cache.backends.db import DatabaseCache
from django.core.cache.backends.locmem import LocMemCache
from django.core.cache.backends.memcached import MemcachedCache, PyLibMCCache
from django.utils import log
from django.conf import settings



logger = log.getLogger("django-tools.SmoothCache")
if not logger.handlers:
    # ensures we don't get any 'No handlers could be found...' messages
    logger.addHandler(log.NullHandler())

if "runserver" in sys.argv or "tests" in sys.argv:
    log.logging.basicConfig(format='%(created)f pid:%(process)d %(message)s')
    logger.setLevel(log.logging.DEBUG)
#    logger.addHandler(log.logging.StreamHandler())


AUTOUPDATECACHE_CHANGE_TIME = getattr(settings, "AUTOUPDATECACHE_CHANGE_TIME", "AUTOUPDATECACHE_CHANGE_TIME")
AUTOUPDATECACHE_UPDATE_TIMESTAMP = getattr(settings, "AUTOUPDATECACHE_UPDATE_TIMESTAMP", 10)
AUTOUPDATECACHE_TIMES = getattr(settings, "AUTOUPDATECACHE_TIMES", (
    # load value, max age in sec.
    (0, 10), #     < 0.5     -> 10sec
    (0.5, 30), #   0.5 - 1.0 -> 30sec
    (1.0, 60), #   1.0 - 1.5 ->  1Min
    (1.5, 120), #  1.5 - 2.0 ->  2Min
    (2.0, 300), #  2.0 - 3.0 ->  5Min
    (3.0, 900), #  3.0 - 4.0 -> 15Min
    (4.0, 3600), # > 4.0     ->  1h
))

# Sort from biggest to lowest:
AUTOUPDATECACHE_TIMES = list(AUTOUPDATECACHE_TIMES)
AUTOUPDATECACHE_TIMES.sort(reverse=True)
AUTOUPDATECACHE_TIMES = tuple(AUTOUPDATECACHE_TIMES)


def get_max_age(load_average):
    """ return max age for the given load average. """
    load_average += 0.1
    for load, max_age in AUTOUPDATECACHE_TIMES:
        if load_average > load:
            break
    return max_age


class _SmoothCache(object):
    __CHANGE_TIME = None # Timestamp of the "last update"
    __NEXT_SYNC = None # Point in the future to update the __CHANGE_TIME

    def __init__(self, *args, **kwargs):
        super(_SmoothCache, self).__init__(*args, **kwargs)
        self._smooth_clear = None

    def __get_change_time(self):
        """
        return current "last change" timestamp.
        To save cache access, update the timestamp only in  
        AUTOUPDATECACHE_UPDATE_TIMESTAMP frequency from cache.
        """
        now = time.time()
        if now > self.__NEXT_SYNC or self.__CHANGE_TIME is None:
            # Update timestamp we must look for a new change time from cache:
            self.__NEXT_SYNC = now + AUTOUPDATECACHE_UPDATE_TIMESTAMP

            change_time = self.get(AUTOUPDATECACHE_CHANGE_TIME)
            if change_time is None:
                logger.debug("CHANGE_TIME is None")
                self.__save_change_time() # save change time into cache             
            elif change_time > self.__CHANGE_TIME:
                self.__CHANGE_TIME = change_time
                logger.debug("update change time to: %r" % change_time)
        else:
            logger.debug("Use old CHANGE_TIME %r" % self.__CHANGE_TIME)

        return self.__CHANGE_TIME

    def __must_updated(self, key, create_time):
        """
        return True if given cache create time is older than the "last change"
        time, but only if the additional time from system load allows it.
        """
        last_change_time = self.__get_change_time()
        if last_change_time < create_time:
            logger.debug(
                "Cache item %r not out-dated (added %s, last change: %s)" % (
                    key, create_time, last_change_time
            ))
            return False

        outdate_age = last_change_time - create_time
        load_average = os.getloadavg()[0] # load over last minute
        max_age = get_max_age(load_average)
        if outdate_age > max_age:
            logger.debug("Out-dated %r (age: %s, max age: %s, load: %s)" % (
                key, outdate_age, max_age, load_average
            ))
            return True

        logger.debug("Keep %r by load (out-dated age: %.2fs, max age: %s, load: %s)" % (
            key, outdate_age, max_age, load_average
        ))
        return False

    def __save_change_time(self):
        """
        save the "last change" timestamp to renew the cache entries in
        self.__CHANGE_TIME and in cache.
        """
        now = int(time.time())
        self.__CHANGE_TIME = now
        self.set(AUTOUPDATECACHE_CHANGE_TIME, now)
        logger.debug("Set CHANGE_TIME to %r" % now)

    #--------------------------------------------------------------------------

    def get(self, key, default=None, version=None):
        value = super(_SmoothCache, self).get(key, default, version)
        if value is None or value is default:
            # Item not in cache
            return value

        try:
            create_time, value = value
            assert isinstance(create_time, float)
        except Exception, err:
            # e.g: entry is saved before smooth cache used.
            logger.error("Can't get 'create_time': %s (Maybe old cache entry)" % err)
            self.delete(key, version)
            return default

        if self.__must_updated(key, create_time):
            # is too old -> delete the item
            self.delete(key, version)
            return default

        return value

    def set(self, key, value, timeout=None, version=None):
        value = (time.time(), value)
        super(_SmoothCache, self).set(key, value, timeout, version)

    def clear(self):
        logger.debug("SmoothCache clear called.")
        self.__save_change_time()


class SmoothFileBasedCache(_SmoothCache, FileBasedCache):
    pass

class SmoothDatabaseCache(_SmoothCache, DatabaseCache):
    pass

class SmoothLocMemCache(_SmoothCache, LocMemCache):
    pass

class SmoothMemcachedCache(_SmoothCache, MemcachedCache):
    pass

class SmoothPyLibMCCache(_SmoothCache, PyLibMCCache):
    pass

#!/usr/bin/env python
# encoding: utf-8
"""
datastore.py

Created by Chris Mulligan on 2010-05-09.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

import uuid
import importlib
from string import letters, digits
from random import choice

def shortkey():
    firstlast = list(letters + digits)
    middle = firstlast + list('-_')
    return ''.join((choice(firstlast), choice(middle), choice(middle), choice(middle), choice(firstlast)))

def init_datastore(config):
    """
    Take the config definition and initialize the datastore.

    The config must contain either a 'datastore' parameter, which
    will be simply returned, or
    must contain a 'factory' which is a callable or entry
    point definition. The callable should take the remainder of
    the params in config as kwargs and return a DataStore instance.
    """
    if 'datastore' in config:
        # the datastore has already been initialized, just use it.
        return config['datastore']
    factory = config.pop('factory')
    if isinstance(factory, basestring):
        "a string like 'package.module:Class'"
        module_name, _, factory_name = factory.partition(':')
        module = importlib.import_module(module_name)
        factory = getattr(module, factory_name)
    return factory(**config)

class DataStore(object):
    """Implements a datastore using an arbitrary backend. """
    def __init__(self, *args, **kwargs):
        pass

    def _store(self, uid, content, data):
        """Store the given dict of content at uid. Nothing returned."""
        raise NotImplementedError

    def _storeLog(self, nick, time, uid):
        """Adds the nick & uid to the log for a given time/order. No return."""
        raise NotImplementedError

    def _retrieve(self, uid):
        """Return a dict with the contents of the paste, including the raw
        data, if any, as the key 'data'. Must pass in uid, not shortid."""
        raise NotImplementedError

    def lookup(self, nick):
        """Looks for the most recent paste by a given nick.
        Returns the uid or None"""
        raise NotImplementedError

    def store(self, type, nick, time, fmt=None, code=None, filename=None, mime=None, data=None, makeshort=True):
        """Store code or a file. Returns a tuple containing the uid and shortid"""
        uid = str(uuid.uuid4())
        if makeshort:
            shortid = shortkey()
        else:
            shortid = None

        temp = {'uid': uid, 'shortid': shortid, 'type': type, 'nick': nick, 'time': time,
            'fmt': fmt, 'code': code,
            'filename': filename, 'mime': mime}
        paste = {}
        for k, v in temp.items():
            if v:
                paste[k] = v
        self._store(uid, paste, data)
        if nick:
            self._storeLog(nick, time, uid)
        return (uid, shortid)

    def retrieve(self, id):
        """Retrieve a paste. Returns a dictionary containing all metadata
        and the file data, if it's a file."""
        if len(id) < 10:
            shortid = id
            uid = self._lookupUid(shortid)
        else:
            uid = id
        return self._retrieve(uid)

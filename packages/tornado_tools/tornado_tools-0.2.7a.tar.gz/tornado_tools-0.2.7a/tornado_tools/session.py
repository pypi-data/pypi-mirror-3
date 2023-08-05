#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Gregory Sitnin <sitnin@gmail.com>"
__copyright__ = "Gregory Sitnin, 2011"


from uuid import uuid1


SessionException = Exception


class AbstractSession(object):
    def __init__(self, conn, session_id=None, auto=True, collection="sessions"):
        self._data = dict()
        self._conn = conn
        self._collection = collection
        self._session_id = session_id if session_id else unicode(uuid1())
        self._auto = auto
        logging.debug("Session initialization: %s"%self._session_id)
        if self._auto:
            self.load()

    def id(self):
        return self._session_id

    def save(self):
        raise SessionException("Concrete .save() method is not implemented")

    def load(self):
        raise SessionException("Concrete .load() method is not implemented")

    def get(self, key, default=None):
        return self._data[key] if self._data.has_key(key) else default

    def set(self, key, value):
        logging.debug("SESSION DATA: %s"%pprint.pformat(self._data))
        self._data[key] = value
        if self._auto:
            self.save()
        return value

    def delete(self, key):
        del self._data[key]
        if self._auto:
            self.save()

try:
    import pymongo

    class MongoSession(AbstractSession):
        def save(self):
            self._conn[self._collection].save({"_id": self._session_id}, self._data)

        def load(self):
            loaded = self._conn[self._collection].find_one({"_id": self._session_id})
            self._data = loaded if loaded else dict()

except ImportError:
    pass

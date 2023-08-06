#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Gregory Sitnin <sitnin@gmail.com>"
__copyright__ = "Gregory Sitnin, 2011"


from uuid import uuid1
from datetime import datetime


SessionException = Exception


class AbstractSession(object):
    def __init__(self, conn, session_id=None, auto=True, update_activity=False, collection="sessions"):
        self._data = dict()
        self._conn = conn
        self._collection = collection
        self._session_id = session_id if session_id else unicode(uuid1())
        self._auto = auto
        self._update_activity = update_activity
        if self._auto:
            self.load()

    def id(self):
        return self._session_id

    def save(self):
        raise SessionException("Concrete .save() method is not implemented")

    def load(self):
        raise SessionException("Concrete .load() method is not implemented")

    def exists(self):
        raise SessionException("Concrete .exists() method is not implemented")

    def destroy(self):
        raise SessionException("Concrete .destroy() method is not implemented")

    def update_activity(self):
        if self._update_activity:
            self._data["last_activity"] = datetime.utcnow()

    def get(self, key, default=None):
        return self._data[key] if self._data.has_key(key) else default

    def set(self, key, value):
        self._data[key] = value
        self.update_activity()
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
            s = self._data
            s["_id"] = self._session_id
            self._conn[self._collection].save(s)

        def load(self):
            loaded = self._conn[self._collection].find_one({"_id": self._session_id})
            self._data = loaded if loaded else dict()

        def destroy(self):
            self._data = dict()
            self._conn[self._collection].remove({"_id": self._session_id})

        def exists(self):
            session = self._conn[self._collection].find_one({"_id": self._session_id}, {"_id": 1})
            return True if session else False

except ImportError:
    pass

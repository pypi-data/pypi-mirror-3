import pymongo
import bson

from datastore import DataStore

class MongoDBDataStore(pymongo.Connection, DataStore):
    def _store(self, uid, content, data):
        """Store the given dict of content at uid. Nothing returned."""
        doc = dict(uid=uid, data=bson.Binary(data))
        doc.update(content)
        self.librarypaste.pastes.save(doc)

    def _storeLog(self, nick, time, uid):
        """Adds the nick & uid to the log for a given time/order. No return."""
        query = dict(uid=uid)
        update = {'$set': dict(nick=nick, time=time)}
        self.librarypaste.pastes.update(query, update)

    def _retrieve(self, uid):
        """Return a dict with the contents of the paste, including the raw
        data, if any, as the key 'data'. Must pass in uid, not shortid."""
        query = dict(uid=uid)
        return self.librarypaste.pastes.find_one(query)

    def lookup(self, nick):
        """Looks for the most recent paste by a given nick.
        Returns the uid or None"""
        query = dict(nick=nick)
        order = dict(time=pymongo.DESCENDING)
        recs = self.librarypaste.pastes.find(query).order(order).limit(1)
        try:
            return next(recs)['uid']
        except StopIteration:
            pass

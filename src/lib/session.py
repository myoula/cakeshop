#!/usr/bin/env python
#coding=utf8

import pickle
import hmac
import uuid
import hashlib
import time
import logging


class MemcacheSessionStore:
    def __init__(self, mcc_connection, **options):
        self.options = {
            'key_prefix': 'session',
            'expire': 7200,
            }
        self.options.update(options)
        self.mcc = mcc_connection

    def prefixed(self, sid):
        return '%s:%s' % (self.options['key_prefix'], sid)

    def generate_sid(self):
        return uuid.uuid4().get_hex()

    def _generate_id(self):
        new_id = hashlib.sha256(self.secret + str(uuid.uuid4()))
        return new_id.hexdigest()

    def _generate_hmac(self, session_id):
        return hmac.new(session_id, self.secret, hashlib.sha256).hexdigest()

    def get_session(self, sid, name):
        data = self.mcc.get(self.prefixed(sid))
        session = pickle.loads(data) if data else {}
        return session

    def set_session(self, sid, session_data, name, expiry=None):
        # key, val, time
        expiry = expiry or self.options['expire']
        if expiry:
            self.mcc.set(self.prefixed(sid), pickle.dumps(session_data), expiry)

    def delete_session(self, sid):
        self.mcc.delete(self.prefixed(sid))

class Session:

    def __init__(self, session_store, session_id=None, expires_days=None):
        self._store = session_store
        self._sid = session_id if session_id else self._store.generate_sid()
        self._dirty = False
        self.set_expires(expires_days)
        try:
            self._data = self._store.get_session(self._sid, 'data')
        except :
            logging.error('Can not connect Memcache Server')
            self._data = {}

    def clear(self):
        self._store.delete_session(self._sid)

    @property
    def id(self):
        return self._sid

    def access(self, remote_ip):
        access_info = {'remote_ip': remote_ip, 'time:':'%.6f' % time.time()}
        self._store.set_session(
            self._sid,
            'last_access',
            pickle.dumps(access_info)
        )

    def last_access(self):
        access_info = self._store.get_session(self._sid, 'last_access')
        return pickle.loads(access_info)

    def set_expires(self, days):
        self._expires = days * 86400 if days else None

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        self._dirty = True

    def __delitem__(self, key):
        del self._data[key]
        self._dirty = True

    def __len__(self):
        return len(self._data)

    def __contains__(self, key):
        return key in self._data

    def __iter__(self):
        for key in self._data:
            yield key

    def __repr__(self):
        return self._data.__repr__()

    def __del__(self):
        self.save()

    def save(self):
        if self._dirty:
            self._store.set_session(self._sid, self._data, 'data', self._expires)
            self._dirty = False
    
from datetime import datetime, timedelta


class Cache(object):

    def __init__(self):
        super(Cache, self).__init__()
        self._dict = {}

    def _set(self, key, value, timeout=None):
        if timeout is not None and timeout <= 0:
            self.delete(key)
            return False
        expires = datetime.now() + timedelta(seconds=timeout) if timeout is not None else None
        self._dict[key] = (value, expires)
        return True

    def set(self, key, value, timeout=None):
        self._set(key, value, timeout)

    def get(self, key, default=None):
        value, expires = self._dict.get(key, (None, None))
        if value is None or (expires is not None and datetime.now() >= expires):
            return default
        return value

    def add(self, key, value, timeout=None):
        if self.get(key) is not None:
            return False
        return self._set(key, value, timeout)

    def delete(self, key):
        if key in self._dict: del self._dict[key]

    def clear(self):
        self._dict.clear()

import decimal
import json
import time
import os.path
import threading

from eventlet.db_pool import ConnectionPool


class Config(object):

    def __init__(self, filepath):
        self.filepath = filepath
        self._tables = None
        self._dbconf = None
        self._driver = None
        self._dbmod = None
        self._lock = threading.Lock()
        self._loaded = 0
        self._pool = None
        self._load()

    def _load(self):
        with self._lock:
            if os.path.getmtime(self.filepath) > self._loaded:
                cfg = json.load(open(self.filepath))
                self._tables = cfg['config']
                self._dbconf = cfg['database']
                self.options = cfg.get('options', {})
                self._loaded = time.time()
                driver = self._dbconf.pop('driver', 'MySQLdb')
                if not self._driver or self._driver.__name__ != driver:
                    try:
                        self._driver = __import__(driver)
                    except:
                        print "Failed to load DB driver"
                        raise

                try:
                    self._dbmod = __import__('gvisdata.db.%s' % driver)
                except ImportError:
                    self._dbmod = None

    def _check(self):
        if os.path.getmtime(self.filepath) > self._loaded:
            self._load()

    def get_table(self, table):
        self._check()
        return self._tables.get(table)

    def get_db(self):
        self._check()
        if self.options.get('pool'):
            with self._lock:
                if not self._pool:
                    max_size = int(self.options.get('pool_max', 4))
                    self._pool = ConnectionPool(
                            self._driver,
                            max_size=max_size,
                            **self._dbconf
                            )
                return ConfiguredConnection(self._pool.get())
            return
        return ConfiguredConnection(self._driver.connect(**self._dbconf))

    def fix_value(self, field_type, value):
        if self._dbmod:
            value = self._dbmod.fix(field_type, value)
        if isinstance(value, (decimal.Decimal)):
            return int(value)
        return value


class ConfiguredConnection():

    def __init__(self, connection, pool=None):
        self.connection = connection
        self.pool = pool

    def __enter__(self):
        return self.connection

    def __exit__(self, type, value, traceback):
        if self.pool:
            self.pool.put(self.connection)
        else:
            self.connection.close()

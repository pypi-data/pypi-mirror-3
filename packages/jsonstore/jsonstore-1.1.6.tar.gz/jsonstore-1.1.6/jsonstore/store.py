import os
import itertools
import operator
from datetime import datetime
import time
import re
import sqlite3
from collections import defaultdict
from threading import Lock
import threading
LOCAL = threading.local()

from uuid import uuid4
from simplejson import loads, dumps

from jsonstore.operators import Operator, Equal


class ConflictError(Exception):
    pass


# http://lists.initd.org/pipermail/pysqlite/2005-November/000253.html
def regexp(expr, item):
    p = re.compile(expr)
    return p.match(item) is not None


class EntryManager(object):
    def __init__(self, index='index.db', **kwargs):
        self.index = index
        if not os.path.exists(self.index):
            self._create_table()
        self.lock = defaultdict(Lock)

    # Thread-safe connection manager. Conections are stored in the 
    # ``threading.local`` object, so they can be safely reused in the
    # same thread.
    @property
    def conn(self):
        if not hasattr(LOCAL, 'conns'):
            LOCAL.conns = {}

        if self.index not in LOCAL.conns:
            LOCAL.conns[self.index] = sqlite3.connect(self.index, 
                    detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        #LOCAL.conns[self.index].create_function("REGEXP", 2, regexp)
        return LOCAL.conns[self.index]

    def _create_table(self):
        self.conn.executescript("""
            CREATE TABLE flat (
                id VARCHAR(255),
                updated timestamp,
                position CHAR(255),
                leaf NUMERIC);
            CREATE INDEX position ON flat (position);

            CREATE TABLE store (
                id VARCHAR(255),
                dumps NUMERIC);
            CREATE INDEX id ON store (id);
        """)
        self.conn.commit()

    def create(self, entry=None, **kwargs):
        if entry is None:
            entry = kwargs
        else:
            assert isinstance(entry, dict), "Entry must be instance of ``dict``!"
            entry.update(kwargs)

        # __id__ and __updated__ can be overriden.
        id_ = entry.setdefault('__id__', str(uuid4()))
        curs = self.conn.execute("SELECT id FROM flat WHERE id=?", (id_,))
        if curs.fetchall():
            raise ConflictError('Conflict, the id "%s" already exists!' % id_)
        entry.setdefault('__updated__', datetime_to_iso(datetime.utcnow()))

        # Store entry.
        self.store_entry(entry)
        return entry

    def delete(self, obj=None, **kwargs):
        if obj is None:
            obj = kwargs

        if isinstance(obj, dict):
            entries = self.search(obj)
            keys = [entry['__id__'] for entry in entries]
        else:
            keys = [key]

        for id_ in keys:
            with self.lock[id_]:
                self.delete_entry(id_)

    def update(self, entry=None, condition=lambda old: True, **kwargs): 
        if entry is None:
            entry = kwargs
        else:
            assert isinstance(entry, dict), "Entry must be instance of ``dict``!"
            entry.update(kwargs)

        id_ = entry['__id__']
        with self.lock[id_]:
            old = self.load_entry(id_)
            if not condition(old):
                raise ConflictError("Pre-condition failed!")
            self.delete_entry(id_)
            new = self.create(entry)
        return new

    def search(self, obj=None, size=None, offset=0, count=False, **kwargs):
        """
        Search database using a JSON object.
        
        The idea is here is to flatten the JSON object (the "key"),
        and search the index table for each leaf of the key using
        an OR. We then get those ids where the number of results
        is equal to the number of leaves in the key, since these
        objects match the whole key.
        
        """
        if obj is None:
            obj = kwargs
        else:
            assert isinstance(obj, dict), "Search key must be instance of ``dict``!"
            obj.update(kwargs)

        # Check for id.
        id_ = obj.pop('__id__', None)

        # Flatten the JSON key object.
        pairs = list(flatten(obj))
        pairs.sort()
        groups = itertools.groupby(pairs, operator.itemgetter(0))

        query = ["SELECT DISTINCT id FROM flat"]
        condition = []
        params = []

        # Check groups from groupby, they should be joined within
        # using an OR.
        leaves = 0
        for (key, group) in groups:
            group = list(group)
            subquery = []
            for position, leaf in group:
                params.append(position)
                if not isinstance(leaf, Operator):
                    leaf = Equal(leaf)
                subquery.append("(position=? AND leaf %s)" % leaf)
                params.extend(leaf.params)
                leaves += 1

            condition.append(' OR '.join(subquery))

        # Build query.
        if condition or id_ is not None:
            query.append("WHERE")
        if id_ is not None:
            query.append("id=?")
            params.insert(0, id_)
            if condition:
                query.append("AND")
        if condition:
            # Join all conditions with an OR.
            query.append("(%s)" % " OR ".join(condition))
        if leaves:
            query.append("GROUP BY id HAVING COUNT(*)=%d" % leaves)
        query.append("ORDER BY updated DESC")
        if size is not None:
            query.append("LIMIT %s" % size)
        if offset:
            query.append("OFFSET %s" % offset)
        query = ' '.join(query)

        if count:
            curs = self.conn.execute("SELECT COUNT(*) FROM (%s) AS ITEMS"
                    % query, tuple(params))
            return curs.fetchone()[0]
        else:
            curs = self.conn.execute(query, tuple(params))
            return [ self.load_entry(row[0]) for row in curs ]

    def load_entry(self, id_):
        curs = self.conn.execute("""
            SELECT dumps FROM store WHERE id=?
        """, (id_,))
        return loads(curs.fetchone()[0])

    def store_entry(self, entry):
        # Index entry.
        indexes = [(entry['__id__'], entry['__updated__'], k, v)
                for (k, v) in flatten(entry) if k != '__id__']
        self.conn.executemany("""
            INSERT INTO flat (id, updated, position, leaf)
            VALUES (?, ?, ?, ?);
        """, indexes)
        self.conn.execute("""
            INSERT INTO store (id, dumps)
            VALUES (?, ?);
        """, (entry['__id__'], dumps(entry)))
        self.conn.commit()

    def delete_entry(self, id_):
        self.conn.execute("DELETE FROM flat WHERE id=?;", (id_,))
        self.conn.execute("DELETE FROM store WHERE id=?;", (id_,))
        self.conn.commit()

    def close(self):
        self.conn.close()
        del LOCAL.conns[self.index]


def escape(name):
    try:
        return name.replace('.', '%2E')
    except TypeError:
        return name


def datetime_to_iso(obj):
    try:
        return obj.isoformat().split('.', 1)[0] + 'Z'
    except:
        return obj


def flatten(obj, keys=[]):
    key = '.'.join(keys)
    if isinstance(obj, list):
        for item in obj:
            for pair in flatten(item, keys):
                yield pair
    elif isinstance(obj, dict):
        for k, v in obj.items():
            for pair in flatten(v, keys + [escape(k)]):
                yield pair
    else:
        yield key, obj

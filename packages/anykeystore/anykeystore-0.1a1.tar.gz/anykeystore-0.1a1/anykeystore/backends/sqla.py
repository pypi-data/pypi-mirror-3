from datetime import datetime

from sqlalchemy import Column, MetaData
from sqlalchemy import String, Text, DateTime, Table
from sqlalchemy.sql import select, delete

from anykeystore.compat import pickle
from anykeystore.interfaces import KeyValueStore
from anykeystore.utils import coerce_timedelta


class SQLStore(KeyValueStore):
    """ Simple storage via SQLAlchemy.

    The store will automatically create a table object if one is not
    supplied. The automatically generated table is shown below. If a
    table is supplied directly, it must support the required columns
    `key`, `value`, and `expires`.

    .. code-block:: python
        table = Table(table_name, metadata,
            Column('key', String(200), primary_key=True, nullable=False),
            Column('value', Text(), nullable=False),
            Column('expires', DateTime()),
        )

    :param engine: A SQLAlchemy engine.
    :param table: Optional. The SQLAlchemy Table instance to be used for
                  storage. If this isn't supplied, a table is generated
                  automatically.
    :type table: sqlalchemy.Table
    :param table_name: Optional. The name of the table.
    :param metadata: Optional. The SQLAlchemy MetaData instance to hook the
                 generated table into.
    :type metadata: sqlalchemy.MetaData
    """
    def __init__(self, engine, **kw):
        self.engine = engine
        if 'table' in kw:
            self.table = kw['table']
        else:
            table_name = kw.pop('table_name', 'key_storage')
            meta = kw.pop('metadata', MetaData())
            self.table = Table(table_name, meta,
                Column('key', String(200), primary_key=True, nullable=False),
                Column('value', Text(), nullable=False),
                Column('expires', DateTime()),
            )

    def create(self):
        self.table.create(checkfirst=True, bind=self.engine)

    def retrieve(self, key):
        s = self.table
        data = self.engine.execute(
            select([s.c.value, s.c.expires], s.c.key == key))
        if data:
            value, expires = data
            if expires is None or datetime.utcnow() < expires:
                return pickle.loads(data[0])

    def store(self, key, value, expires=None):
        expiration = None
        if expires:
            expiration = datetime.utcnow() + coerce_timedelta(expires)
        value = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        self.engine.execute(
            self.table.insert(),
            key=key, value=value, expires=expiration)

    def delete(self, key):
        self.engine.execute(delete(self.table, self.table.c.key == key))

    def purge_expired(self):
        self.engine.execute(
            delete(self.table, self.table.c.expires < datetime.utcnow()))

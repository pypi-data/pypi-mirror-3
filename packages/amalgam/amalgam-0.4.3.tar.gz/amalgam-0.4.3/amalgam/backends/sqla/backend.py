from sqlalchemy import create_engine, orm, MetaData
from sqlalchemy.ext import declarative

from amalgam.backends.base.backend import BaseBackend
from amalgam.backends.sqla.columns import SqlaColumns
from amalgam.backends.sqla.base import Base, DeclarativeMeta


class Query(orm.Query):
    @classmethod
    def new(cls, type, *args, **kwargs):
        q = cls(*args, **kwargs)
        if hasattr(type.Meta, 'order_by'):
            q = q.order_by(type.Meta.order_by())
        return q

    def __call__(self, *entities):
        map(self.add_entity, entities)
        return self

    def _add(self, obj, flush):
        self.session.add(obj)
        if flush:
            self.session.flush()

    def _delete(self, obj):
        self.session.delete(obj)

    def joinedload(self, *keys, **kw):
        '''Apply option `joinedload` and return the new Query
        '''
        return self.options(orm.joinedload(*keys, **kw))

    def joinedload_all(self, *keys, **kw):
        '''Apply option `joinedload_all` and return the new Query
        '''
        return self.options(orm.joinedload_all(*keys, **kw))

    def lazyload(self, *keys):
        '''Apply option `lazyload` and return the new Query
        '''
        return self.options(orm.lazyload(*keys))


class QueryProperty(object):
    def __init__(self, mgr):
        self.mgr = mgr

    def __get__(self, obj, type):
        try:
            mapper = orm.class_mapper(type)
            if mapper:
                return Query.new(type, mapper, session=self.mgr.session())
        except orm.exc.UnmappedClassError:
            return


class SABackend(SqlaColumns, BaseBackend):
    '''SQLAlchemy backend

    :param uri:
      URI to database
    :param engine_options:
      Dictionary of options to pass to :py:func:`sqlalchemy.create_engine`
    '''
    def __init__(self, uri, engine_options=None):
        engine_options = engine_options or {}
        self.engine = create_engine(uri, **engine_options)
        self.session = orm.scoped_session(orm.sessionmaker(bind=self.engine))
        self._Base = None
        self.metadata = MetaData()

    def __str__(self):
        return str(self.engine.url)

    def _get_base(self):
        base = declarative.declarative_base(cls=Base,
                                            metaclass=DeclarativeMeta,
                                            metadata=self.metadata)
        base.query = QueryProperty(self)
        return base

    @property
    def Base(self):
        if not self._Base:
            self._Base = self._get_base()
        return self._Base

    def __call__(self, tableprefix=None):
        base = self._get_base()
        base.Meta.tableprefix = tableprefix
        return base

    def create_all(self):
        self.metadata.create_all(bind=self.engine)

    def drop_all(self):
        self.metadata.drop_all(bind=self.engine)

    def reflect(self):
        self.metadata.reflect(bind=self.engine)

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def close(self):
        self.session.remove()


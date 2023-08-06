import sqlalchemy as sa
from sqlalchemy import orm

from amalgam.utils import import_attribute
from amalgam.backends.sqla.columns import SqlaColumnMarker


def evaluable(module, path):
    if not isinstance(path, str):
        return path
    if '.' not in path:
        path, name = module, path
    else:
        path, name = path.rsplit('.', 1)
    return "getattr(__import__('%s', {}, {}, ['%s']), '%s')" % (
        path, name, name)


def _resolve_attribute(module, name):
    if not '.' in name:
        name = '%s.%s' % (module, name)
    return import_attribute(name)


def get_target_and_pk(cls, name, column):
    target = column.kwargs.pop('target')
    target_pk = None

    if isinstance(target, basestring):
        target = _resolve_attribute(cls.__module__, target)

    for c in target.__table__.columns:
        if c.primary_key:
            target_pk = c
            break

    if target_pk is None:
        raise TypeError("Target model '%s.%s' has no primary key" %
                        (target.__module__, target.__name__))

    return target, target_pk


def fk_processor(cls, pk, name, column):
    target, target_pk = get_target_and_pk(cls, name, column)

    relkw = column.kwargs.pop('relkw', {})
    relkw.setdefault('lazy', column.kwargs.pop('lazy', 'select'))
    column_type = column.kwargs.pop('type', None)
    column_name = column.kwargs.pop('name', '%s_id' % name)

    column.kwargs.setdefault('nullable', False)
    column.kwargs.setdefault('index', True)
    col = sa.Column(column_type, sa.ForeignKey(target_pk), **column.kwargs)
    yield column_name, col

    # have lazy backreference by default
    if isinstance(relkw.get('backref'), str):
        relkw['backref'] = orm.backref(relkw['backref'], lazy='dynamic')

    yield name, orm.relationship(target, primaryjoin=col==target_pk, **relkw)


def o2o_processor(cls, pk, name, column):
    target, target_pk = get_target_and_pk(cls, name, column)

    relkw = column.kwargs.pop('relkw', {})
    relkw.setdefault('lazy', column.kwargs.pop('lazy', 'select'))
    column_type = column.kwargs.pop('type', None)
    column_name = column.kwargs.pop('name', '%s_id' % name)

    backref = relkw.pop('backref', None)
    if backref is not None:
        if isinstance(backref, str):
            backref = orm.backref(backref, uselist=False)
        else:
            backref.kwargs['uselist'] = False
    else:
        relkw['uselist'] = False


    column.kwargs.setdefault('nullable', False)
    column.kwargs.setdefault('index', True)
    col = sa.Column(column_type, sa.ForeignKey(target_pk), **column.kwargs)
    yield column_name, col

    yield name, orm.relationship(target, backref=backref,
                                 primaryjoin=col==target_pk, **relkw)


def m2m_processor(cls, pk, name, column):
    target, target_pk = get_target_and_pk(cls, name, column)

    through = column.kwargs.pop('through')

    ltype = column.kwargs.pop('ltype', None)
    rtype = column.kwargs.pop('rtype', None)

    ownid = '%s_id' % cls.__tablename__
    relid = '%s_id' % target.__tablename__

    if not through:
        table = sa.Table('%s_%s' % (cls.__tablename__, target.__tablename__),
                         cls.metadata,
                         sa.Column(ownid,
                                   ltype,
                                   sa.ForeignKey(pk),
                                   index=True, nullable=False),
                         sa.Column(relid,
                                   rtype,
                                   sa.ForeignKey(target_pk),
                                   index=True, nullable=False)
                         )
    else:
        table = "%s.__table__" % evaluable(cls.__module__, through)

    # be lazy by default
    if 'lazy' not in column.kwargs:
        column.kwargs['lazy'] = 'dynamic'
    # match laziness in backreference
    if isinstance(column.kwargs.get('backref'), str):
        column.kwargs['backref'] = orm.backref(column.kwargs['backref'],
                                               lazy=column.kwargs['lazy'])

    yield name, orm.relationship(target, secondary=table, **column.kwargs)


PROCESSORS = {'ForeignKey': fk_processor,
              'OneToOne': o2o_processor,
              'ManyToMany': m2m_processor}

def findpk(columns):
    for c in columns:
        if isinstance(c, sa.Column) and c.primary_key:
            return c

def preprocess(cls, bases, attrs):
    '''Model class preprocessor

    Is a generator yielding tuples of 3 values:

     - name of the field
     - value (field, postprocessor or None)
     - indicator if this is postprocessor

    None as the returned value is indicator that should name should be deleted
    from attrs. Postprocessor indicates that given value should be called with a
    newly created class.
    '''
    pk = findpk(attrs.itervalues())
    if pk is None:
        for base in bases:
            if hasattr(base, '__table__'):
                pk = findpk(base.__table__.columns)
                if pk is not None:
                    break

    if 'id' in attrs and pk is None:
        raise TypeError("%r does not have primary key, but has 'id' attribute"
                        % cls)

    if pk is None:
        pk = sa.Column(sa.Integer, primary_key=True)
        # TODO: Find more appropriate fix for making 'id' first column. Two
        # options, actually: this hack or making our own declarative wrapper
        pk._creation_order = 0
        yield 'id', pk

    for name, c in list(attrs.iteritems()): # copy explicitly
        if isinstance(c, SqlaColumnMarker):
            # it should fail if there is unknown marker
            for resname, resval in PROCESSORS[c.name](cls, pk, name, c):
                yield resname, resval

import sqlalchemy as sa

from amalgam.backends.base.columns import BaseColumns


class SqlaColumnMarker(object):
    def __init__(self, markername, *args, **kwargs):
        self.name = markername
        self.args = args
        self.kwargs = kwargs


class SqlaColumns(BaseColumns):
    @staticmethod
    def String(max_length, type=sa.Unicode, *args, **kwargs):
        return sa.Column(type(max_length), *args, **kwargs)

    @staticmethod
    def Text(max_length=None, type=sa.UnicodeText, *args, **kwargs):
        return sa.Column(type(max_length), *args, **kwargs)

    @staticmethod
    def Boolean(*args, **kwargs):
        return sa.Column(sa.Boolean, *args, **kwargs)

    @staticmethod
    def Integer(*args, **kwargs):
        return sa.Column(sa.Integer, *args, **kwargs)

    @staticmethod
    def Float(*args, **kwargs):
        return sa.Column(sa.Float, *args, **kwargs)

    @staticmethod
    def Decimal(*args, **kwargs):
        return sa.Column(sa.DECIMAL, *args, **kwargs)

    @staticmethod
    def DateTime(*args, **kwargs):
        return sa.Column(sa.DateTime, *args, **kwargs)

    @staticmethod
    def Date(*args, **kwargs):
        return sa.Column(sa.Date, *args, **kwargs)

    @staticmethod
    def Time(*args, **kwargs):
        return sa.Column(sa.Time, *args, **kwargs)

    @staticmethod
    def Serialized(encode=None, decode=None, *args, **kwargs):
        '''Create a column for serialized data

        :param encode:
          Encoder of data to serialized format
        :param decode:
          Decoder of data from serialized format

        See other arguments in help of :py:class:`sqlalchemy.schema.Column`
        '''
        if not encode and not decode:
            return sa.Column(sa.PickleType(), *args, **kwargs)
        if not encode or not decode:
            raise ValueError("Both 'encode' and 'decode' should be specified")
        class Serializer(object):
            dumps = encode
            loads = decode
        return sa.Column(sa.PickleType(pickler=Serializer()),
                         *args, **kwargs)

    @staticmethod
    def ForeignKey(target, backref=None, relkw=None, *args, **kwargs):
        '''Create a foreign key relationship

        :param backref:
          name of a property to be placed on a related model
        :param relkw:
          keyword arguments for :py:func:`sqlalchemy.orm.relationship`
        :param name='%(name)s_id':
          name of column
        :param type='sqlalchemy.Integer()':
          column type
        :param lazy='select':
          specifies how related items should be loaded. *Not* replicated to
          backref. See more in help of :py:func:`sqlalchemy.orm.relationship`.

        See other arguments in help of :py:class:`sqlalchemy.schema.Column`
        '''
        relkw = relkw or {}
        relkw['backref'] = backref
        return SqlaColumnMarker('ForeignKey', target=target,
                                relkw=relkw, *args, **kwargs)

    @staticmethod
    def OneToOne(target, backref=None, relkw=None, *args, **kwargs):
        '''Create a one to one foreign key relationship

        :param backref:
          name of a property to be placed on a related model
        :param relkw:
          keyword arguments for :py:func:`sqlalchemy.orm.relationship`
        :param name='%(name)s_id':
          name of column
        :param type=sqlalchemy.Integer():
          column type
        :param lazy='select':
          specifies how related items should be loaded. *Not* replicated to
          backref. See more in help of :py:func:`sqlalchemy.orm.relationship`.

        See other arguments in help of :py:class:`sqlalchemy.schema.Column`
        '''
        relkw = relkw or {}
        relkw['backref'] = backref
        return SqlaColumnMarker('OneToOne', target=target,
                                relkw=relkw, *args, **kwargs)

    @staticmethod
    def ManyToMany(target, through=None, *args, **kwargs):
        '''Create a many to many relationship

        :param through:
          optional predefined intermediary table, which will be created
          automatically if not supplied. If supplied, should contain foreign
          keys to both ends of relationship

        :param backref:
          name of a property to be placed on a related model or a
          :py:func:`sqlalchemy.orm.backref` object itself

        :param lazy='dynamic':
          specifies how related items should be loaded. Replicated to backref if
          it was not a ready object. See more in help of
          :py:func:`sqlalchemy.orm.relationship`.

        See other arguments in help of :py:func:`sqlalchemy.orm.relationship`
        '''
        return SqlaColumnMarker('ManyToMany', target=target,
                                through=through, *args, **kwargs)

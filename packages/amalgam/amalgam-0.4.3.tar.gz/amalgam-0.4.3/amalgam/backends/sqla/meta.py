from ordereddict import OrderedDict
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.orm.interfaces import MANYTOMANY, MANYTOONE, ONETOMANY
from sqlalchemy.orm import RelationshipProperty

from amalgam.metabase import ModelMetaData
from amalgam.utils import classproperty


class Meta(object):
    @classproperty
    def columns(meta):
        columns = OrderedDict()

        # Base classes don't have mappers
        if not hasattr(meta.cls, '__mapper__'):
            return

        # Process columns and collect relations
        for v in meta.cls.__mapper__.iterate_properties:
            n = v.key

            if isinstance(v, ColumnProperty):
                # Grab column
                c = v.columns[len(v.columns) - 1]

                # Check if foreign key
                foreign_key = False
                if c.foreign_keys:
                    foreign_key = True

                # Check if max_length is present
                max_length = None
                if hasattr(c.type, 'length'):
                    max_length = c.type.length

                columns[n] = ModelMetaData(c.type.__class__.__name__,
                                                c,
                                                n,
                                                primary_key = c.primary_key,
                                                foreign_key = foreign_key,
                                                max_length = max_length,
                                                nullable = c.nullable,
                                                default = c.default and c.default.arg,
                                                unique = c.unique)

            elif isinstance(v, RelationshipProperty):
                # Create entry
                if v.direction is MANYTOONE:
                    name = 'ForeignKey'

                    # Special check for backref's uselist
                    if v.backref is not None and not isinstance(v.backref, str):
                        # SQLA 0.5 check
                        if hasattr(v, 'kwargs') and v.backref.kwargs.get('uselist'):
                                name = 'OneToOne'
                        # SQLA 0.6 check
                        elif (isinstance(v.backref, tuple)
                              and v.backref[1].get('uselist')):
                                name = 'OneToOne'
                elif v.direction is ONETOMANY:
                    name = 'OneToMany'

                    # If not using list, then it is OneToOne
                    if not v.uselist:
                        name = 'OneToOne'
                elif v.direction is MANYTOMANY:
                    name = 'ManyToMany'
                else:
                    raise 'Unsupported relation direction type %s' % (
                        v.direction.name)

                #if v.uselist == False:
                #    name = 'OneToOne'
                if v.secondary is not None and v.uselist:
                    name = 'ManyToMany'

                # TODO: Check if argument can be callable
                r = v.argument

                if not isinstance(r, basestring):
                    # Hack to get relation target
                    if not hasattr(r, '__name__'):
                        r = r.__class__

                    target = '%s.%s' % (r.__module__, r.__name__)
                else:
                    target = r

                if not '.' in target:
                    target = '%s.%s' % (r.__module__, target)

                columns[n] = ModelMetaData(name,
                                                v,
                                                n,
                                                nullable = False,
                                                relation = True,
                                                target = target)
        return columns


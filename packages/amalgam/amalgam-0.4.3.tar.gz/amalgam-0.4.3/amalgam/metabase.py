class ModelMetaData(object):
    def __init__(self, field_type, field, name,
                 nullable=True, max_length=None, relation=False,
                 primary_key=False, foreign_key=False,
                 default=None, unique=False, **kwargs):
        self.field_type = field_type
        self.field = field
        self.name = name
        self.nullable = nullable
        self.max_length = max_length

        self.relation = relation
        self.primary_key = primary_key
        self.foreign_key = foreign_key

        self.default = default
        self.unique = unique

        self.props = kwargs

    def __repr__(self):
        return '%s column metadata' % (self.field_type)

import inspect


class Mapping(object):
    creation_counter = 0

    def __init__(self, query=None, name=None, static_value=None, default=None, transform=None):
        self.creation_order = Mapping.creation_counter
        Mapping.creation_counter += 1
        self.name = name
        self.default = default
        self.transform = transform if transform else lambda x: x

        if query and static_value:
            raise AttributeError('Define either query or static_value')

        if query:
            if callable(query):
                self._do_mapping = lambda context: query(context)
            else:
                self.query_list = query.split('/')
                self.query_list_len = len(self.query_list)

        self.static_value = static_value

    @staticmethod
    def _value_or_call(obj):
        return obj() if callable(obj) else obj

    def map(self, context):
        return self._do_mapping(context)

    def _do_mapping(self, context):
        if self.static_value:
            return self.static_value

        current_context = context
        for i, e in enumerate(self.query_list, 1):
            current_context = current_context.get(e)
            if i == self.query_list_len or not current_context:
                return self.transform(current_context) if current_context is not None else Mapping._value_or_call(self.default)


class MapperMeta(type):
    def __new__(meta, classname, bases, classDict):
        cls = type.__new__(meta, classname, bases, classDict)
        cls.mappings = sorted(inspect.getmembers(cls, lambda o: isinstance(o, Mapping)), key=lambda i: i[1].creation_order)
        for name, mapping in cls.mappings:
            if isinstance(mapping, Mapping):
                if not mapping.name:
                    mapping.name = name

        cls.nb_mappings = len(cls.mappings)
        return cls


class MapperBase(object):
    __metaclass__ = MapperMeta


class Mapper(MapperBase):

    def headers(self):
        return [n.capitalize().replace('_', ' ') for n, v in self.mappings]

    def map(self, inp):
        """
        Performs mapping on a sequence of dict objects and returns the corresponding rows:
        >>> class TestMapper(Mapper):
        >>>     name = Mapping('name')
        >>>     value = Mapping('value')
        >>> mapper = TestMapper()
        >>> res = mapper.map([{'name': 'test name', 'value': 'test value'}, {'name': 'test name 2', 'value': 'test value 2'}])
        returns
        [('test name', 'test value'), ('test name 2', 'test value 2')]
        """
        result = []
        for record in inp:
            row = []
            for _, mapping in self.mappings:
                row.append(mapping.map(record))
            result.append(row)
        return result

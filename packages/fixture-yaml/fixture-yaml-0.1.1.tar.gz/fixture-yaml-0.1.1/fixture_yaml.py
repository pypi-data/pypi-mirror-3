import os.path
import yaml


__all__ = ['YAMLSet']


class YAMLSetMeta(type):
    """
    Creates an individual subclass for every YAML dataset,
    because fixture expects every dataset to be an individual class.
    """
    def __call__(self, *args, **kw):
        # XXX to avoid recursion
        if not getattr(self, '_instrumented', False):
            storable_name = YAMLSet.get_storable_name(*args, **kw)
            new_class = type('YAMLSet.%s' % storable_name, (YAMLSet,), {})
            new_class._instrumented = True
            instance = new_class(*args, **kw)
        else:
            instance = super(YAMLSetMeta, self).__call__(*args, **kw)
        return instance


class YAMLSet(object):
    """
    A dataset that loads its data from a YAML file.
    """

    __metaclass__ = YAMLSetMeta

    def __init__(self, filepath, storable_name=None):
        """
        ``filepath``
            A path to an appropriate YAML file.

        ``storable_name``
            The name of the storable object that the loader should fetch from
            its env to load this dataset with.  If omitted, the name
            is constructed from the filename, e.g. "user.yml" -> "User".
        """
        self.ref = []
        self._data = yaml.load(open(filepath, 'r'))
        self.meta = Meta()
        self.meta.storable_name = (
            self.get_storable_name(filepath, storable_name=storable_name))

    @staticmethod
    def get_storable_name(filepath, storable_name=None):
        if storable_name is None:
            filename = os.path.basename(filepath)
            storable_name = os.path.splitext(filename)[0].title()
        return storable_name

    def __iter__(self):
        for k, w in self._data.iteritems():
            yield k, Row(w)

    def data(self):
        return list(self._data.iteritems())

    def __getattr__(self, name):
        if not name.startswith('_') and name in self._data:
            return Row(self._data[name])
        raise AttributeError(name)

    def shared_instance(self, **kw):
        """
        Returns or creates the singleton instance for this class
        """
        return self

    def _setdata(self, k, v):
        """
        Appears to be part of public :class:`fixture.DataSet` API.
        """
        pass


class Row(object):
    """
    Represents a dataset row.
    """
    def __init__(self, data):
        self._data = data

    def __getattr__(self, name):
        return self._data[name]

    def __call__(self, name):
        return self

    def columns(self, **kw):
        return self._data.keys()


class Meta(object):
    """
    Mocks :class:`fixture.DataSet.Meta`.
    """
    keys = []
    data = {}
    references = []
    storable = None
    storable_name = None
    storage_medium = None

    class StoredObjects(list):
        def store(self, k, v):
            pass

    _stored_objects = StoredObjects()

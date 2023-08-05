"""Dedun result classes.
"""

import anyjson

from dedun import exceptions


class ResultBase(object):
    """This class is the base of all generated Result classes."""
    def __init__(self, data):
        """data must be an dictionary with the contents of the result."""
        self._data = data

    def __getattr__(self, key):
        """Returns an data attribute or DedunError if the attribute is not
        found."""
        try:
            return self._data[key]
        except KeyError:
            raise exceptions.DedunError('Attribute "%s" does not exist.' % key)

    def get_attributes(self):
        """Returns a list of all attributes of a Result object."""
        return self._data.keys()

    def get_json(self):
        """Returns the result as JSON."""
        return anyjson.serialize(self._data)

    def __repr__(self):
        """Returns the canonical string representation of the object."""
        try:
            u = unicode(self)
        except (UnicodeEncodeError, UnicodeDecodeError):  # pragma: no cover
            u = '[Bad Unicode data]'
        return '%s: %s' % (self.__class__.__name__, u.encode('utf-8'))

    def __unicode__(self):
        """Returns a unicode object using self.name_attributes."""
        attributes = [getattr(self, name) for name in self.name_attributes]
        return u' '.join(attributes)


class Results(object):
    """A list of results."""
    def __init__(self, data, resource):
        """Creates a new Results object.

        data must a a string of JSON data.
        resource must be an instance of ResourceBase.
        """
        deserialized = anyjson.deserialize(data)
        if 'error' in deserialized:
            raise exceptions.DedunError(deserialized['error'])
        self._data = deserialized['data']
        self._resource = resource

    def _get_result_class(self):
        """Returns the right Result class for the current resource."""
        if not hasattr(self, '_result_class'):
            klass = self._resource.path.title().replace('/', '')
            self._result_class = type('%sResult' % klass, (ResultBase,),
                {'name_attributes': self._resource.name_attributes})
        return self._result_class

    def count(self):
        """Returns the number of objects in the result list."""
        return len(self._data)

    def order_by(self, *attrs):
        """Changes the order the Result objects.

        You can use one or more attributes to order by.
        Returns an instance of self.
        """
        for attr in attrs:
            if attr not in self[0].get_attributes():
                attr_error = 'Result has no attribute %s!' % attr
                raise exceptions.DedunError(attr_error)
        self._data = self._sort(self._data, *attrs)
        return self

    @classmethod
    def _sort(cls, data, *attrs):
        """Orders the data dictionary by the list of keys."""
        from operator import itemgetter
        return sorted(data, key=itemgetter(*attrs))

    def reverse(self):
        """Reverses the order of the Result objects."""
        self._data.reverse()

    def __len__(self):
        """Returns the number of objects in the result list."""
        return self.count()

    def __getitem__(self, key):
        """Returns a single Result object or a slice of objects."""
        if isinstance(key, slice):
            return [self._get_result_class()(self._data[i])
                for i in range(*key.indices(len(self)))]
        else:
            try:
                return self._get_result_class()(self._data[key])
            except (KeyError, IndexError):
                raise exceptions.ObjectNotFound('Item not found.')

    def __repr__(self):
        """Returns the canonical string representation of the object."""
        return '%d %s items' % (self.count(), self._resource.path)

    def __iter__(self):
        """Iterates over the list of Result objects."""
        for item in self._data:
            yield self._get_result_class()(item)

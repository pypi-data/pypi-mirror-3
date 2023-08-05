# *-* encoding: utf-8 *-*
"""Dedun is a Python client for the RESTful API of API.Leipzig . This API
gives access to the public data of the city of Leipzig.
"""

import urllib
import urllib2
from urlparse import urljoin

import anyjson

__version__ = (0, 2, 5, 'final', 0)

DEDUN_URL = 'http://www.apileipzig.de/api/%s/'

DEDUN_VERSION = 'v1'


class DedunError(Exception):
    """Main exception class."""
    pass


class ObjectNotFound(DedunError):
    """This exception is raised if an object/item can not be found."""
    pass


class ImproperlyConfigured(DedunError):
    """This exception is raised on configuration errors."""
    pass


class MultipleResults(DedunError):
    """This exception is raised on multiple results.

    That is, if a get request returns more than one result.
    """
    def __str__(self):
        return 'Your query had multiple results.'


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
            raise DedunError('Attribute "%s" does not exist.' % key)

    def get_attributes(self):
        """Returns a list of all attributes of a Result object."""
        return self._data.keys()

    def __repr__(self):
        """Returns the canonical string representation of the object."""
        try:
            u = unicode(self)
        except (UnicodeEncodeError, UnicodeDecodeError):
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
            raise DedunError(deserialized['error'])
        self._data = deserialized['data']
        self._resource = resource
        self._reversed = False

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
        """
        for attr in attrs:
            if attr not in self[0].get_attributes():
                raise DedunError('Result has no attribute %s!' % attr)
        from operator import itemgetter
        self._data = sorted(self._data, key=itemgetter(*attrs))
        return self

    def reverse(self):
        """Reverses the order of the Result objects."""
        self._reversed = not self._reversed

    def __len__(self):
        """Returns the number of objects in the result list."""
        return self.count()

    def __getitem__(self, key):
        """Returns a single Result object."""
        try:
            return self._get_result_class()(self._data[key])
        except (KeyError, IndexError):
            raise ObjectNotFound('Item not found.')

    def __getslice__(self, i, j):
        """Returns a slice of result objects."""
        slice = []
        for item in self._data[i:j]:
            slice.append(self._get_result_class()(item))
        return slice

    def __repr__(self):
        """Returns the canonical string representation of the object."""
        return '%d %s items' % (self.count(), self._resource.path)

    def __iter__(self):
        """Iterates over the list of Result objects."""
        if self._reversed:
            iterator = reversed(self._data)
        else:
            iterator = self._data
        for item in iterator:
            yield self._get_result_class()(item)


class ResourceBase(object):
    """Base Resource class used by all Resource objects."""
    def __init__(self, api_key='', path=None, debug=False):
        """Creates a new Resource object.

        Use api_key to set your API Leipzig key.
        You can use path to set a path string for experimental new Resources.
        Set debug=True to enable debugging.
        """
        if hasattr(self, 'path') and path:
            raise ImproperlyConfigured(
                "Don't specify a path when using %s." %
                self.__class__.__name__)
        if path:
            self.path = path
        self._api_key = api_key
        self._debug = debug
        self._url = urljoin(DEDUN_URL % DEDUN_VERSION, self.path)
        self._format = 'json'

    def all(self):
        """Returns all objects of this Resource."""
        return self._query()

    def get(self, **kwargs):
        """Returns one object of this Resource.

        You have to give one keyword argument to find the object.
        """
        if not len(kwargs) == 1:
            raise DedunError('You have to give exactly one argument.')
        if 'limit' in kwargs:
            raise DedunError('There is no sense in using limit with get.')
        if 'offset' in kwargs:
            raise DedunError('There is no sense in using offset with get.')
        try:
            result = self.search(**kwargs)
            if result.count() > 1:
                raise MultipleResults()
            item = result[0]
        except IndexError:
            raise ObjectNotFound('Item not found.')
        return item

    def search(self, **kwargs):
        """Returns a list of objects.

        You can search for objects by giving one or more keyword arguments.
        Use limit and offset to limit the results.
        """
        if len(kwargs) == 0:
            raise DedunError('You have to give at least one search argument.')
        kwargs['search'] = 'search'
        return self._query(**kwargs)

    def _query(self, **kwargs):
        """Generates the URL and sends the HTTP request to the API."""
        url = self._url
        search = kwargs.pop('search', '')
        if search:
            url = urljoin(url + '/', search)
        kwargs['api_key'] = self._api_key
        kwargs['format'] = self._format
        encoded_args = urllib.urlencode(kwargs)
        url = url + '?' + encoded_args
        if self._debug:
            import sys
            sys.stdout.write(url + '\n')
        response = urllib2.urlopen(url).read()
        return Results(response, self)


class CalendarEvents(ResourceBase):
    """Mediahandbook Events Resource"""
    path = 'calendar/events'
    name_attributes = ('name',)


class CalendarHosts(ResourceBase):
    """Calendar Hosts Resource"""
    path = 'calendar/hosts'
    name_attributes = ('first_name', 'last_name')


class CalendarVenues(ResourceBase):
    """Calendar Venues Resource"""
    path = 'calendar/venues'
    name_attributes = ('name',)


class DistrictDistricts(ResourceBase):
    """District Districts Resource"""
    path = 'district/districts'
    name_attributes = ('name',)


class DistrictIhkcompanies(ResourceBase):
    """District Ihkcompanies Resource"""
    path = 'district/ihkcompanies'
    name_attributes = ('district_id',)


class DistrictStatistics(ResourceBase):
    """District Statistics Resource"""
    path = 'district/statistics'
    name_attributes = ('district_id',)


class DistrictStreets(ResourceBase):
    """District Streets Resource"""
    path = 'district/streets'
    name_attributes = ('name',)


class MediahandbookBranches(ResourceBase):
    """Mediahandbook Branches Resource"""
    path = 'mediahandbook/branches'
    name_attributes = ('name',)


class MediahandbookCompanies(ResourceBase):
    """Mediahandbook Companies Resource"""
    path = 'mediahandbook/companies'
    name_attributes = ('name',)


class MediahandbookPeople(ResourceBase):
    """Mediahandbook People Resource"""
    path = 'mediahandbook/people'
    name_attributes = ('first_name', 'last_name')

"""Dedun resource classes.
"""

from urllib import urlencode
from urllib2 import urlopen
from urlparse import urljoin

from dedun import settings
from dedun import exceptions
from dedun.results import Results

__all__ = ['CalendarEvents', 'CalendarHosts', 'CalendarVenues',
    'DistrictDistricts', 'DistrictIhkcompanies', 'DistrictStatistics',
    'DistrictStreets', 'MediahandbookBranches', 'MediahandbookCompanies',
    'MediahandbookPeople']


class ResourceBase(object):
    """Base Resource class used by all Resource objects."""
    def __init__(self, api_key='', path=None, debug=False):
        """Creates a new Resource object.

        Use api_key to set your API Leipzig key.
        You can use path to set a path string for experimental new Resources.
        Set debug=True to enable debugging.
        """
        if hasattr(self, 'path') and path:
            raise exceptions.ImproperlyConfigured(
                "Don't specify a path when using %s." %
                self.__class__.__name__)
        if path:
            self.path = path
        self._api_key = api_key
        self._debug = debug
        self._url = urljoin(settings.API_URL % settings.API_VERSION,
            self.path)
        self._format = 'json'

    def all(self):
        """Returns all objects of this Resource."""
        return self._query()

    def get(self, **kwargs):
        """Returns one object of this Resource.

        You have to give one keyword argument to find the object.
        """
        if not len(kwargs) == 1:
            kwargs_error = 'You have to give exactly one argument.'
            raise exceptions.DedunError(kwargs_error)
        if 'limit' in kwargs:
            limit_error = 'There is no sense in using limit with get.'
            raise exceptions.DedunError(limit_error)
        if 'offset' in kwargs:
            offset_error = 'There is no sense in using offset with get.'
            raise exceptions.DedunError(offset_error)
        result = self.search(**kwargs)
        if result.count() > 1:
            raise exceptions.MultipleResults()
        return result[0]

    def search(self, **kwargs):
        """Returns a list of objects.

        You can search for objects by giving one or more keyword arguments.
        Use limit and offset to limit the results.
        """
        if len(kwargs) == 0:
            kwargs_error = 'You have to give at least one search argument.'
            raise exceptions.DedunError(kwargs_error)
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
        encoded_args = urlencode(kwargs)
        url = url + '?' + encoded_args
        if self._debug:
            import sys
            sys.stdout.write(url + '\n')
        response = urlopen(url).read()
        return Results(response, self)


class CalendarEvents(ResourceBase):
    """Calendar Events Resource"""
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

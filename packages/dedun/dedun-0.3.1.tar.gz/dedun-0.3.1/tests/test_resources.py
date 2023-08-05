"""Tests for resources module.
"""
import pytest

from dedun import exceptions
from dedun.resources import MediahandbookCompanies, ResourceBase
from dedun.results import ResultBase, Results


class TestResource():
    def test_path(self):
        test_path = 'test/resource'
        res = ResourceBase(path=test_path)
        assert test_path == res.path

    def test_path_improperly_configured(self):
        with pytest.raises(exceptions.ImproperlyConfigured):
            MediahandbookCompanies(path='test/fails')

    @pytest.mark.localserver
    def test_debug(self, apihttpserver, capsys):
        key = '42'
        companies = MediahandbookCompanies(api_key=key, debug=True)
        companies.all()
        out, err = capsys.readouterr()
        debugout = '%s/v1/%s?api_key=%s&format=json\n' % (apihttpserver.url, companies.path, key)
        assert out == debugout

    @pytest.mark.localserver
    def test_all(self, apihttpserver):
        assert isinstance(MediahandbookCompanies().all(), Results)

    @pytest.mark.localserver(single=True)
    def test_get(self, apihttpserver):
        assert isinstance(MediahandbookCompanies().get(id=1), ResultBase)

    def test_get_args_error(self):
        with pytest.raises(exceptions.DedunError):
            MediahandbookCompanies().get()

    def test_get_limit_error(self):
        with pytest.raises(exceptions.DedunError):
            MediahandbookCompanies().get(limit=10)

    def test_get_offset_error(self):
        with pytest.raises(exceptions.DedunError):
            MediahandbookCompanies().get(offset=20)

    @pytest.mark.localserver
    def test_get_multiple_results_error(self, apihttpserver):
        with pytest.raises(exceptions.MultipleResults):
            MediahandbookCompanies().get(name='design')

    @pytest.mark.localserver(empty=True)
    def test_get_not_found_error(self, apihttpserver):
        with pytest.raises(exceptions.ObjectNotFound):
            MediahandbookCompanies().get(id=1)

    @pytest.mark.localserver
    def test_search(self, apihttpserver):
        companies = MediahandbookCompanies()
        assert isinstance(companies.search(name='design'), Results)

    def test_search_no_args_error(self):
        with pytest.raises(exceptions.DedunError):
            MediahandbookCompanies().search()

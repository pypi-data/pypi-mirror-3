"""Tests for results module.
"""
import pytest

from dedun import exceptions
from dedun.resources import MediahandbookCompanies
from dedun.results import ResultBase, Results
from tests import utils


class TestResult:
    def setup_method(self, method):
        json, json_obj = utils.load_fixture('mediahandbook_companies.json')
        self.json_obj = json_obj['data'][0]
        self.result = Results(json, MediahandbookCompanies())[0]

    def test_getattr(self):
        assert self.json_obj['name'] == self.result.name
        assert isinstance(self.result.name, unicode)

    def test_attr_does_not_exist(self):
        with pytest.raises(exceptions.DedunError):
            self.result.does_not_exist

    def test_get_attributes(self):
        assert self.json_obj.keys() == self.result.get_attributes()
        assert isinstance(self.result.get_attributes(), list)

    def test_get_json(self):
        import anyjson
        json = anyjson.serialize(self.json_obj)
        assert json == self.result.get_json()
        assert isinstance(self.result.get_json(), str)

    def test_repr(self):
        assert self.result.__class__.__name__ in self.result.__repr__()
        assert unicode(self.result).encode('utf-8') in repr(self.result)
        assert isinstance(repr(self.result), str)

    def test_unicode(self):
        assert self.json_obj['name'] == unicode(self.result)
        assert isinstance(unicode(self.result), unicode)


class TestResults:
    def setup_method(self, method):
        json, json_obj = utils.load_fixture('mediahandbook_companies.json')
        self.json_obj = json_obj['data']
        self.results = Results(json, MediahandbookCompanies())

    def test_deserialization_error(self):
        json = '{"error": "Item does not exist."}'
        with pytest.raises(exceptions.DedunError):
            Results(json, MediahandbookCompanies())

    def test_count(self):
        assert len(self.json_obj) == self.results.count()

    def test_len(self):
        assert len(self.json_obj) == len(self.results)

    def test_sort(self, setupnames):
        names = setupnames
        data = [names.bremer, names.bauer, names.maier, names.werner]
        data_sorted = [names.werner, names.bremer, names.bauer, names.maier]
        assert data_sorted == Results._sort(data, 'city')

    def test_sort_by_two_keys(self, setupnames):
        names = setupnames
        data = [names.bremer, names.bauer, names.maier, names.werner]
        data_sorted = [names.werner, names.bauer, names.bremer, names.maier]
        assert data_sorted == Results._sort(data, 'city', 'name')

    def test_order_by(self):
        self.results.order_by('name')
        json_obj = Results._sort(self.json_obj, 'name')
        i = 0
        for result in self.results:
            assert json_obj[i] == result._data
            i += 1

    def test_order_by_two_fields(self):
        self.results.order_by('name', 'postcode')
        json_obj = Results._sort(self.json_obj, 'name', 'postcode')
        i = 0
        for result in self.results:
            assert json_obj[i] == result._data
            i += 1

    def test_order_by_error(self):
        with pytest.raises(exceptions.DedunError):
            self.results.order_by('no_name')

    def test_reverse(self):
        i = 9
        self.results.reverse()
        for result in self.results:
            assert self.json_obj[i] == result._data
            i -= 1
        i = 0
        self.results.reverse()
        for result in self.results:
            assert self.json_obj[i] == result._data
            i += 1

    def test_result_class(self):
        result_class = 'MediahandbookCompaniesResult'
        assert self.results[0].__class__.__name__ == result_class
        assert isinstance(self.results[0], ResultBase)

    def test_getitem(self):
        assert self.json_obj[0] == self.results[0]._data

    def test_getitem_reverted(self):
        self.results.reverse()
        assert self.json_obj[-1] == self.results[0]._data

    def test_object_not_found(self):
        with pytest.raises(exceptions.ObjectNotFound):
            self.results[11]

    def test_getslice(self):
        i = 0
        for result in self.results[:5]:
            assert self.json_obj[i] == result._data
            i += 1

    def test_getslice_reverted(self):
        # See issue #1: Slicing does not respect reverse() method.
        i = 9
        self.results.reverse()
        for result in self.results[:5]:
            assert self.json_obj[i] == result._data
            i -= 1

    def test_getslice_len(self):
        assert len(self.json_obj[:5]) == len(self.results[:5])

    def test_getslice_type(self):
        assert isinstance(self.results[:5], list)

    def test_repr(self):
        assert str(self.results.count()) in self.results.__repr__()
        assert isinstance(repr(self.results), str)

    def test_iter(self):
        i = 0
        for result in self.results:
            assert self.json_obj[i] == result._data
            i += 1

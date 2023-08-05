# *-* encoding: utf-8 *-*
import pytest

from dedun import settings
from tests import utils


def pytest_funcarg__setupnames(request):
    """Returns a Names object with several identities for testing.

    Each identity has a name and a city attribute.
    """
    class Names(object):
        def __init__(self):
            self.bauer = {'city': u'Hamburg', 'name': u'Bauer'}
            self.bremer = {'city': u'Hamburg', 'name': u'Bremer'}
            self.maier = {'city': u'München', 'name': u'Maier'}
            self.werner = {'city': u'Berlin', 'name': u'Werner'}
    return Names()


def pytest_funcarg__apihttpserver(request):
    """Returns a httpserver instance.

    Creates a httpserver instance which serves a JSON fixture. Monkeypatches
    the dedun.settings so the httpserver instance is used for all requests.

    The localserver marker can be used to pass arguments to configure the JSON
    fixture:

    * ``@pytest.mark.localserver(empty=True)`` - Loads an empty fixture.
    * ``@pytest.mark.localserver(single=True)`` - Loads a single fixture.
    """
    localserver = request.keywords.get('localserver', False)
    if localserver and localserver.kwargs.get('single', False):
        json, json_obj = utils.load_fixture('mediahandbook_company.json')
    elif localserver and localserver.kwargs.get('empty', False):
        json = '{"data": []}'
    else:
        json, json_obj = utils.load_fixture('mediahandbook_companies.json')
    httpserver = request.getfuncargvalue('httpserver')
    httpserver.serve_content(json)
    monkeypatch = request.getfuncargvalue('monkeypatch')
    monkeypatch.setattr(settings, 'API_URL', httpserver.url + '/%s/')
    return httpserver


def pytest_addoption(parser):
    parser.addoption('--no-localserver', action='store_true', default=False,
        help='Skips tests using the local HTTP server.')


def pytest_runtest_setup(item):
    """Skips tests using the local HTTP server.

    Skips all tests marked with "localserver" depending on pytest_localserver
    if the package is missing.
    Skips all tests marked with "localserver" if the --no-localserver option
    is used.
    """
    if getattr(item.obj, 'localserver', False):
        pytest.importorskip('pytest_localserver')
        if item.config.getvalue('no_localserver'):
            pytest.skip('Skipping tests using local HTTP server.')

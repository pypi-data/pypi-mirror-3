"""Dedun is a Python client for the RESTful API of API.Leipzig . This API
gives access to the public data of the city of Leipzig.
"""

__version__ = (0, 3, 0, 'final', 0)

# Wildcard import is used to be backwards compatible.
# pylint: disable=W0401
from dedun.resources import *

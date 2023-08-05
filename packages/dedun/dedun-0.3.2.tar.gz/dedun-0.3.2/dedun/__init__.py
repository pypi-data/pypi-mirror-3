"""Dedun is a Python client for the RESTful API of API.Leipzig . This API
gives access to the public data of the city of Leipzig.
"""

from warnings import warn

__version__ = (0, 3, 2, 'final', 0)

# Wildcard import is used for backwards compatibly.
# pylint: disable=W0401
try:
    from dedun.resources import *
    warn('Please use dedun.resources instead of dedun.', DeprecationWarning)
except ImportError:  # pragma: no cover
    pass

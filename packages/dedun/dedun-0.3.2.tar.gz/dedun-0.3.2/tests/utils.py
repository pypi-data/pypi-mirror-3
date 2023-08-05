"""Test helpers.
"""
import os

import anyjson


def load_fixture(filename):
    """Loads a fixture from a file.

    Returns the contents as string and JSON object."""
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path) as fixture:
        json_str = fixture.read()
        json_obj = anyjson.deserialize(json_str)
    return (json_str, json_obj)

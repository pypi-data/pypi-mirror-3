"""Dedun exceptions.
"""


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
        return 'Your query had multiple results.'  # pragma: no cover

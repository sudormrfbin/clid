#!/usr/bin/env python3

"""
clid.exceptions
~~~~~~~~~~~

Exceptions.
"""


class ClidError(Exception):
    """Base class for all Clid exceptions."""


class ClidUserError(ClidError):
    """Exception raised due to user's behavior."""


class InvalidTagError(ClidUserError):
    """Exception raised when there is an invalid tag used."""


class UnknownFileTypeError(ClidUserError):
    """
    Exception raised when filetype is unknown and hence tags cannot be read.
    """

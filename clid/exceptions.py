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

#!/usr/bin/env python3

"""
clid.errors
~~~~~~~~~~~

Exceptions.
"""


class ClidError(Exception):
    """Base class for all Clid exceptions."""

    pass


class ClidUserError(ClidError):
    """Exception raised due to user's behavior."""

    pass

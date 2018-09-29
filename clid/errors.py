#!/usr/bin/env python3

"""Exceptions used by Clid"""


class ClidError(Exception):
    """Base class for all Clid exceptions."""

    pass


class ClidUserError(ClidError):
    """Exception raised due to user's behavior."""

    pass

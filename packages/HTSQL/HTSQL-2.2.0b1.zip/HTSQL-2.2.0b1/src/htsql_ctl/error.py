#
# Copyright (c) 2006-2011, Prometheus Research, LLC
# See `LICENSE` for license information, `AUTHORS` for the list of authors.
#


"""
:mod:`htsql_ctl.error`
======================

This module implements exceptions raised by command-line scripts.
"""


class ScriptError(Exception):
    """
    A fatal application error.

    `detail`
        The error message.
    """

    kind = """Fatal error"""

    def __init__(self, detail):
        assert isinstance(detail, str)
        self.detail = detail

    def __str__(self):
        return "%s: %s\n" % (self.kind, self.detail)

    def __repr__(self):
        return "<%s.%s %s>" % (self.__class__.__module__,
                               self.__class__.__name__, self)



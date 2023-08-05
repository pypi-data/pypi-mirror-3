#
# Copyright (c) 2006-2011, Prometheus Research, LLC
# See `LICENSE` for license information, `AUTHORS` for the list of authors.
#


"""
:mod:`htsql_engine.sqlite.connect`
==================================

This module implements the connection adapter for SQLite.
"""


from htsql.connect import Connect, Normalize, DBError
from htsql.adapter import adapts
from htsql.context import context
from htsql.domain import (BooleanDomain, StringDomain, DateDomain, TimeDomain,
                          DateTimeDomain)
import sqlite3
import datetime


class SQLiteError(DBError):
    """
    Raised when a database error occurred.
    """


def sqlite3_power(x, y):
    try:
        return float(x) ** float(y)
    except:
        return None


class ConnectSQLite(Connect):
    """
    Implementation of the connection adapter for SQLite.
    """

    def open_connection(self, with_autocommit=False):
        # FIXME: should we complain if the database address or
        # authentications parameters are not `None`?
        # Get the path to the database file.
        db = context.app.htsql.db
        # Generate and return the DBAPI connection.
        if with_autocommit:
            connection = sqlite3.connect(db.database, isolation_level=None)
        else:
            connection = sqlite3.connect(db.database)
        self.create_functions(connection)
        return connection

    def create_functions(self, connection):
        connection.create_function('POWER', 2, sqlite3_power)

    def normalize_error(self, exception):
        # If we got a DBAPI exception, generate our error out of it.
        if isinstance(exception, sqlite3.Error):
            message = str(exception)
            error = SQLiteError(message, exception)
            return error

        # Otherwise, let the superclass return `None`.
        return super(ConnectSQLite, self).normalize_error(exception)


class NormalizeSQLiteBoolean(Normalize):

    adapts(BooleanDomain)

    def __call__(self, value):
        if value is None:
            return None
        return (value != 0)


class NormalizeSQLiteString(Normalize):

    adapts(StringDomain)

    def __call__(self, value):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return value


class NormalizeSQLiteDate(Normalize):

    adapts(DateDomain)

    def __call__(self, value):
        if isinstance(value, (str, unicode)):
            converter = sqlite3.converters['DATE']
            value = converter(value)
        return value


class NormalizeSQLiteTime(Normalize):

    adapts(TimeDomain)

    def __call__(self, value):
        if isinstance(value, (str, unicode)):
            hour, minute, second = value.split(':')
            hour = int(hour)
            minute = int(minute)
            if '.' in second:
                second, microsecond = second.split('.')
                second = int(second)
                microsecond = int(microsecond)
            else:
                second = int(second)
                microsecond = 0
            value = datetime.time(hour, minute, second, microsecond)
        return value


class NormalizeSQLiteDateTime(Normalize):

    adapts(DateTimeDomain)

    def __call__(self, value):
        if isinstance(value, (str, unicode)):
            converter = sqlite3.converters['TIMESTAMP']
            value = converter(value)
        return value



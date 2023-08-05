#
# Copyright (c) 2006-2011, Prometheus Research, LLC
# See `LICENSE` for license information, `AUTHORS` for the list of authors.
#


"""
:mod:`htsql_engine.sqlite.connect`
==================================

This module implements the connection adapter for SQLite.
"""


from htsql.connect import Connect, Normalize, NormalizeError, DBError
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

    def open(self):
        # FIXME: should we complain if the database address or
        # authentications parameters are not `None`?
        # Get the path to the database file.
        db = context.app.htsql.db
        # Generate and return the DBAPI connection.
        connection = sqlite3.connect(db.database)
        self.create_functions(connection)
        if self.with_autocommit:
            connection.isolation_level = None
        return connection

    def create_functions(self, connection):
        connection.create_function('POWER', 2, sqlite3_power)


class NormalizeSQLiteError(NormalizeError):

    def __call__(self):
        # If we got a DBAPI exception, generate our error out of it.
        if isinstance(self.error, sqlite3.Error):
            message = str(self.error)
            error = SQLiteError(message)
            return error
        # Otherwise, let the superclass return `None`.
        return super(NormalizeSQLiteError, self).__call__()


# FIXME: validate numeric values.


class NormalizeSQLiteBoolean(Normalize):

    adapts(BooleanDomain)

    @staticmethod
    def convert(value):
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if not isinstance(value, int):
            raise SQLiteError("expected a Boolean value, got %r" % value)
        return (value != 0)


class NormalizeSQLiteString(Normalize):

    adapts(StringDomain)

    @staticmethod
    def convert(value):
        if value is None:
            return None
        if isinstance(value, str):
            value = value.decode('utf-8')
        if not isinstance(value, unicode):
            value = unicode(value)
        return value


class NormalizeSQLiteDate(Normalize):

    adapts(DateDomain)

    @staticmethod
    def convert(value):
        if value is None:
            return None
        if isinstance(value, datetime.date):
            return value
        if not isinstance(value, (str, unicode)):
            raise SQLiteError("expected a date value, got %r" % value)
        converter = sqlite3.converters['DATE']
        value = converter(value)
        return value


class NormalizeSQLiteTime(Normalize):

    adapts(TimeDomain)

    @staticmethod
    def convert(value):
        if value is None:
            return None
        if isinstance(value, datetime.time):
            return value
        if not isinstance(value, (str, unicode)):
            raise SQLiteError("expected a time value, got %r" % value)
        # FIXME: verify that the value is in valid format.
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

    @staticmethod
    def convert(value):
        if value is None:
            return None
        if isinstance(value, datetime.datetime):
            return value
        if not isinstance(value, (str, unicode)):
            raise SQLiteError("expected a timestamp value, got %r" % value)
        converter = sqlite3.converters['TIMESTAMP']
        value = converter(value)
        return value



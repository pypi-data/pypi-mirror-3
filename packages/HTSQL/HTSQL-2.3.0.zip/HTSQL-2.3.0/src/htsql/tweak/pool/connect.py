#
# Copyright (c) 2006-2012, Prometheus Research, LLC
#


from __future__ import with_statement
from ...core.adapter import weigh
from ...core.context import context
from ...core.connect import Connect


class PoolConnect(Connect):

    weigh(1.0)

    def __call__(self):
        if self.with_autocommit:
            return super(PoolConnect, self).__call__()
        addon = context.app.tweak.pool
        with addon.lock:
            for connection in addon.items[:]:
                if not connection.is_valid:
                    addon.items.remove(connection)
            for connection in addon.items:
                if not connection.is_busy:
                    connection.acquire()
                    return connection
            connection = super(PoolConnect, self).__call__()
            addon.items.append(connection)
            return connection



#
# Copyright (c) 2006-2012, Prometheus Research, LLC
#


from __future__ import with_statement
from ...core.context import context
from ...core.cache import once
from ...core.adapter import adapts, named
from ...core.cmd.command import ProducerCmd, DefaultCmd
from ...core.cmd.act import Act, ProduceAction, act
from ...core.tr.fn.bind import BindCommand
from ...core.tr.signature import UnarySig
from ...core.tr.bind import bind
from ...core.tr.syntax import QuerySyntax, SegmentSyntax
from ...core.tr.binding import CommandBinding
from ...core.tr.error import BindError
from ...core.tr.lookup import lookup_command
import weakref


@once
def get_slave_app():
    from htsql import HTSQL
    master = weakref.ref(context.app)
    slave = HTSQL(None, {'tweak.meta.slave': {'master': master}})
    return slave


class MetaCmd(ProducerCmd):

    def __init__(self, syntax, environment=None):
        self.syntax = syntax
        self.environment = environment


class BindMeta(BindCommand):

    named('meta')
    signature = UnarySig

    def expand(self, op):
        if not isinstance(op, SegmentSyntax):
            raise BindError("a segment is required", op.mark)
        op = QuerySyntax(op, op.mark)
        command = MetaCmd(op, environment=self.state.environment)
        return CommandBinding(self.state.scope, command, self.syntax)


class ProduceMeta(Act):

    adapts(MetaCmd, ProduceAction)

    def __call__(self):
        slave_app = get_slave_app()
        with slave_app:
            binding = bind(self.command.syntax,
                           environment=self.command.environment)
            command = lookup_command(binding)
            if command is None:
                command = DefaultCmd(binding)
            product = act(command, self.action)
        return product



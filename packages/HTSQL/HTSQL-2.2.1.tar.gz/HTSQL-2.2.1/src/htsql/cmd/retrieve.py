#
# Copyright (c) 2006-2011, Prometheus Research, LLC
# See `LICENSE` for license information, `AUTHORS` for the list of authors.
#


from ..adapter import adapts, Utility
from ..util import Record
from .command import RetrieveCmd, SQLCmd
from .act import (analyze, Act, ProduceAction, SafeProduceAction,
                  AnalyzeAction, RenderAction)
from ..tr.encode import encode
from ..tr.flow import OrderedFlow
from ..tr.rewrite import rewrite
from ..tr.compile import compile
from ..tr.assemble import assemble
from ..tr.reduce import reduce
from ..tr.dump import serialize
from ..tr.lookup import guess_name
from ..connect import DBError, Connect, normalize
from ..error import EngineError


class ElementProfile(object):

    def __init__(self, binding):
        self.binding = binding
        self.name = guess_name(binding)
        if self.name is not None:
            self.name = self.name.encode('utf-8')
        self.domain = binding.domain
        self.syntax = binding.syntax
        self.mark = binding.mark


class SegmentProfile(object):

    def __init__(self, binding):
        self.binding = binding
        self.name = guess_name(binding)
        if self.name is not None:
            self.name = self.name.encode('utf-8')
        self.syntax = binding.syntax
        self.mark = binding.mark
        self.elements = [ElementProfile(element)
                         for element in binding.elements]


class RequestProfile(object):

    def __init__(self, plan):
        self.plan = plan
        self.binding = plan.binding
        self.syntax = plan.syntax
        self.mark = plan.mark
        self.segment = None
        if plan.frame.segment is not None:
            self.segment = SegmentProfile(plan.binding.segment)


class Product(Utility):

    def __init__(self, profile, records=None):
        self.profile = profile
        self.records = records

    def __iter__(self):
        if self.records is not None:
            return iter(self.records)
        else:
            return iter([])

    def __nonzero__(self):
        return (self.records is not None)


class ProduceRetrieve(Act):

    adapts(RetrieveCmd, ProduceAction)

    def __call__(self):
        binding = self.command.binding
        expression = encode(binding)
        # FIXME: abstract it out.
        if isinstance(self.action, SafeProduceAction):
            limit = self.action.limit
            expression = self.safe_patch(expression, limit)
        expression = rewrite(expression)
        term = compile(expression)
        frame = assemble(term)
        frame = reduce(frame)
        plan = serialize(frame)
        profile = RequestProfile(plan)
        records = None
        if plan.sql:
            assert profile.segment is not None
            normalizers = []
            for element in profile.segment.elements:
                normalizers.append(normalize(element.domain))
            record_name = profile.segment.name
            element_names = [element.name
                             for element in profile.segment.elements]
            record_class = Record.make(record_name, element_names)
            connection = None
            try:
                connect = Connect()
                connection = connect()
                cursor = connection.cursor()
                cursor.execute(plan.sql.encode('utf-8'))
                records = []
                for row in cursor:
                    values = []
                    for item, normalizer in zip(row, normalizers):
                        value = normalizer(item)
                        values.append(value)
                    records.append(record_class(*values))
                connection.commit()
                connection.release()
            except DBError, exc:
                raise EngineError("failed to execute a database query: %s"
                                  % exc)
            except:
                if connection is not None:
                    connection.invalidate()
                raise
        return Product(profile, records)

    def safe_patch(self, expression, limit):
        segment = expression.segment
        if segment is None:
            return expression
        flow = segment.flow
        while not flow.is_axis:
            if (isinstance(flow, OrderedFlow) and flow.limit is not None
                                              and flow.limit <= limit):
                return expression
            flow = flow.base
        if flow.is_root:
            return expression
        if isinstance(segment.flow, OrderedFlow):
            flow = segment.flow.clone(limit=limit)
        else:
            flow = OrderedFlow(segment.flow, [], limit, None, segment.binding)
        segment = segment.clone(flow=flow)
        expression = expression.clone(segment=segment)
        return expression


class AnalyzeRetrieve(Act):

    adapts(RetrieveCmd, AnalyzeAction)

    def __call__(self):
        binding = self.command.binding
        expression = encode(binding)
        expression = rewrite(expression)
        term = compile(expression)
        frame = assemble(term)
        frame = reduce(frame)
        plan = serialize(frame)
        return plan


class RenderSQL(Act):

    adapts(SQLCmd, RenderAction)
    def __call__(self):
        plan = analyze(self.command.producer)
        status = '200 OK'
        headers = [('Content-Type', 'text/plain; charset=UTF-8')]
        body = []
        if plan.sql:
            body = [plan.sql.encode('utf-8')]
        return (status, headers, body)



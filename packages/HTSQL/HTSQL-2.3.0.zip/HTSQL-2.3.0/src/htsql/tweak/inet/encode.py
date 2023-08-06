#
# Copyright (c) 2006-2012, Prometheus Research, LLC
#


from ...core.adapter import adapts, adapts_many
from ...core.domain import IntegerDomain, StringDomain
from ...core.tr.encode import Convert
from ...core.tr.flow import CastCode
from .domain import INetDomain


class ConvertINet(Convert):

    adapts_many((IntegerDomain, INetDomain),
                (StringDomain, INetDomain),
                (INetDomain, IntegerDomain),
                (INetDomain, StringDomain))

    def __call__(self):
        return CastCode(self.state.encode(self.base), self.domain,
                        self.binding)


class ConvertINetToINet(Convert):

    adapts(INetDomain, INetDomain)

    def __call__(self):
        return self.state.encode(self.base)



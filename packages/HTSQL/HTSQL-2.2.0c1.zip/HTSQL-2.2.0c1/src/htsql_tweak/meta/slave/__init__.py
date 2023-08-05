#
# Copyright (c) 2006-2011, Prometheus Research, LLC
# See `LICENSE` for license information, `AUTHORS` for the list of authors.
#


from . import connect
from htsql.addon import Addon, Parameter
from htsql.util import DB
from htsql.validator import ClassVal


class TweakMetaSlaveAddon(Addon):

    name = 'tweak.meta.slave'
    hint = """implement meta database (auxiliary)"""

    prerequisites = []
    postrequisites = ['htsql']
    parameters = [
            Parameter('master', ClassVal(object)),
    ]

    @classmethod
    def get_extension(cls, app, attributes):
        return { 'htsql': { 'db': DB(engine='sqlite',
                                     database=':meta:',
                                     username=None,
                                     password=None,
                                     host=None, port=None) },
                 'engine.sqlite': {} }



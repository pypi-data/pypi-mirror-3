#
# Copyright (c) 2006-2011, Prometheus Research, LLC
# See `LICENSE` for license information, `AUTHORS` for the list of authors.
#


"""
:mod:`htsql.application`
========================

This module implements an HTSQL application.
"""


from __future__ import with_statement
from .context import context
from .addon import Addon
from .adapter import ComponentRegistry
from .util import maybe, oneof, listof, dictof, tupleof
from .wsgi import WSGI
import pkg_resources


class Application(object):
    """
    Implements an HTSQL application.

    `db`
        The connection URI.

    `extensions`
        List of addons activated with the application.
    """

    def __init__(self, db, *extensions):
        assert isinstance(list(extensions),
                listof(oneof(str,
                             tupleof(str, maybe(dictof(str, object))),
                             dictof(str, maybe(dictof(str, object))))))
        self.addons = []
        htsql_extension = {'htsql': {} }
        if db is not None:
            htsql_extension['htsql']['db'] = db
        extensions = [htsql_extension] + list(extensions)
        configuration = {}
        dependencies = {}
        addon_class_by_name = {}
        addon_instance_by_name = {}
        while extensions:
            while extensions:
                extension = extensions.pop(0)
                if isinstance(extension, str):
                    extension = { extension: None }
                elif isinstance(extension, tuple):
                    extension = dict([extension])
                for addon_name in sorted(extension):
                    addon_parameters = extension[addon_name]
                    addon_name = addon_name.replace('-', '_')
                    if addon_parameters is None:
                        addon_parameters = {}
                    if addon_name in addon_instance_by_name:
                        if addon_parameters:
                            raise ImportError("invalid addon dependency at %r"
                                              % addon_name)
                        continue
                    configuration.setdefault(addon_name, {})
                    for key in sorted(addon_parameters):
                        value = addon_parameters[key]
                        key = key.replace('-', '_')
                        if key not in configuration[addon_name]:
                            configuration[addon_name][key] = value
                    if addon_name not in addon_class_by_name:
                        entry_points = list(pkg_resources.iter_entry_points(
                                                'htsql.addons', addon_name))
                        if len(entry_points) == 0:
                            raise ImportError("unknown entry point %r"
                                              % addon_name)
                        elif len(entry_points) > 1:
                            raise ImportError("ambiguous entry point %r"
                                              % addon_name)
                        [entry_point] = entry_points
                        addon_class = entry_point.load()
                        if not (isinstance(addon_class, type) and
                                issubclass(addon_class, Addon) and
                                addon_class.name == addon_name):
                            raise ImportError("invalid entry point %r"
                                              % addon_name)
                        addon_class_by_name[addon_name] = addon_class
                        prerequisites = addon_class.get_prerequisites()
                        postrequisites = addon_class.get_postrequisites()
                        requisites_extension = dict((name, {})
                                    for name in prerequisites+postrequisites)
                        if requisites_extension:
                            extensions.append(requisites_extension)
                        dependencies.setdefault(addon_name, [])
                        for name in prerequisites:
                            name = name.replace('-', '_')
                            dependencies[addon_name].append(name)
                        for name in postrequisites:
                            name = name.replace('-', '_')
                            dependencies.setdefault(name, [])
                            dependencies[name].append(addon_name)
            while not extensions and (len(addon_instance_by_name)
                                        < len(addon_class_by_name)):
                for addon_name in sorted(dependencies):
                    dependencies[addon_name] = [name
                                for name in dependencies[addon_name]
                                if name not in addon_instance_by_name]
                candidates = [addon_name
                            for addon_name in sorted(addon_class_by_name)
                            if addon_name not in addon_instance_by_name]
                for addon_name in candidates:
                    if not dependencies[addon_name]:
                        break
                else:
                    raise ImportError("circular addon dependency at %r"
                                      % candidates[0])
                addon_class = addon_class_by_name[addon_name]
                attributes = {}
                valid_attributes = set()
                for parameter in addon_class.parameters:
                    valid_attributes.add(parameter.attribute)
                for key in sorted(configuration[addon_name]):
                    if key not in valid_attributes:
                        raise ImportError("uknown parameter %r of addon %r"
                                          % (key, addon_name))
                for parameter in addon_class.parameters:
                    if parameter.attribute in configuration[addon_name]:
                        value = configuration[addon_name][parameter.attribute]
                        try:
                            value = parameter.validator(value)
                        except ValueError, exc:
                            raise ImportError("invalid parameter %r"
                                              " of addon %r: %s"
                                              % (parameter.attribute,
                                                 addon_name, exc))
                    else:
                        value = parameter.default
                    attributes[parameter.attribute] = value
                extension = addon_class.get_extension(self, attributes)
                if extension:
                    extensions.append(extension)
                addon_instance = addon_class(self, attributes)
                addon_instance_by_name[addon_name] = addon_instance
        for addon_name in sorted(addon_instance_by_name):
            self.addons.append(addon_instance_by_name[addon_name])

    def __enter__(self):
        """
        Activates the application in the current thread.
        """
        context.switch(None, self)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Inactivates the application in the current thread.
        """
        context.switch(self, None)

    def __call__(self, environ, start_response):
        """
        Implements the WSGI entry point.
        """
        with self:
            wsgi = WSGI()
            body = wsgi(environ, start_response)
            for chunk in body:
                yield chunk



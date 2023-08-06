#!/usr/bin/env python

from cli.log import LoggingApp
from cli.app import CommandLineMixin, Application, ArgumentParser
from cli.log import LoggingMixin
from cli._ext.argparse import ArgumentError

class BaseCommandArgumentParser(ArgumentParser):
    def parse_args(self, args=None, namespace=None):
        return self.parse_known_args(args, namespace)

class BaseCommandMixin(object):
    """A Mixing for use with pyCLI that enables the concept of a base
    application that has individualy sub commands that are each an application
    in their own right."""
    argparser_factory = BaseCommandArgumentParser

    def pre_run(self):
        """Custom pre_run logic to preserve argv for parsing by a SubCommand."""
        ns, argv = self.argparser.parse_args()
        self.argv = argv
        self.params = self.update_params(self.params, ns)

    def setup(self):
        """Configure the :class:`CommandLineMixin`.

        During setup, the application instantiates the
        :class:`argparse.ArgumentParser` and adds a version parameter
        (:option:`-V`, to avoid clashing with :option:`-v`
        verbose).
        """
        self.argparser = self.argparser_factory(
            prog=self.name,
            usage=self.usage,
            description=self.description,
            epilog=self.epilog,
            prefix_chars=self.prefix,
            argv=self.argv,
            stdout=self.stdout,
            stderr=self.stderr,
            add_help=False,
            )

        # We add this ourselves to avoid clashing with -v/verbose.
        if self.version is not None:
            self.add_param(
                "-V", "--version", action="version", 
                version=("%%(prog)s %s" % self.version),
                help=("show program's version number and exit"))

class BaseCommandApp(BaseCommandMixin, CommandLineMixin, Application):
    """A pyCLI application that inherits from our :class:`.BaseCommandMixin` as
    well as CommandLineMixin and Application."""

    def __init__(self, main=None, **kwargs):
        CommandLineMixin.__init__(self, **kwargs)
        Application.__init__(self, main, **kwargs)

    def pre_run(self):
        Application.pre_run(self)
        BaseCommandMixin.pre_run(self)

    def setup(self):
        Application.setup(self)
        BaseCommandMixin.setup(self)

class SubCommandMixin(object):
    """A mixin to handle creating a subcommand application."""
    def __init__(self, base=None, **kwargs):
        self.base = base

class SubCommandApp(SubCommandMixin, LoggingApp):
    """A pyCLI application to handle creating applications that are subcommands
    of a :class:`.BaseCommandApp`."""
    def __init__(self, main=None, **kwargs):
        LoggingApp.__init__(self, main, **kwargs)
        SubCommandMixin.__init__(self, **kwargs)
        argv = ['']
        self.base.pre_run()
        argv.extend(self.base.argv)
        self.argv = argv

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4



__all__ = ['add_subparser', 'get_parser']

import argparse

doc="This is the top-level command for the Coopr optimization project."
epilog="""
Coopr supports a variety of modeling and optimization capabilities.
Different tools are executed as subcommands of this command.  Each
subcommand supports independent command-line options.  Use the -h option
to print details for a subcommand.  For example, type

   coopr pyomo -h

to print information about the `pyomo` subcommand.
"""
coopr_parser = argparse.ArgumentParser(description=doc, epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
coopr_subparsers = coopr_parser.add_subparsers(dest='subparser_name', title='subcommands', description='valid subcommands')

def add_subparser(name, **args):
    """Add a subparser to the 'coopr' command."""
    func = None
    if 'func' in args:
        func = args['func']
        del args['func']
    parser = coopr_subparsers.add_parser(name, **args)
    if not func is None:
        parser.set_defaults(func=func)
    return parser

def get_parser():
    """Return the parser used by the 'coopr' commmand."""
    return coopr_parser


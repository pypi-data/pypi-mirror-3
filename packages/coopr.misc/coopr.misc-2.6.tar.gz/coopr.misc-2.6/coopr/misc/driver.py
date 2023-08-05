
import argparse
import coopr_parser
import os
import os.path
import sys
import glob
#import textwrap
import pyutilib.subprocess

def setup_command_parser(parser):
    parser.add_argument("--list", dest="summary", action='store_true', default=False,
                        help="list the active solvers")
    parser.add_argument("command", nargs='*', help="The command and command-line options")

def command_exec(options):
    cmddir = os.path.dirname(os.path.abspath(sys.executable))+os.sep
    if options.summary:
        print ""
        print "The following commands are installed in the Coopr bin directory:"
        print "----------------------------------------------------------------"
        for file in glob.glob(cmddir+'*'):
            print "", os.path.basename(file)
        print ""
        if len(options.command) > 0:
            print "WARNING: ignoring command specification"
        return
    if len(options.command) == 0:
        print "ERROR: no command specified"
        return
    if not os.path.exists(cmddir+options.command[0]):
        print "ERROR: the command '%s' does not exist" % (cmddir+options.command[0])
        return
    pyutilib.subprocess.run(cmddir+' '.join(options.command), tee=True)

def version_exec(options):
    import coopr.coopr
    print "Coopr version "+coopr.coopr.version

#
# Add a subparser for the coopr command
#
setup_command_parser(
    coopr_parser.add_subparser('run',
        func=command_exec, 
        help='Execute a command from the Coopr bin (or Scripts) directory.',
        description='This coopr subcommand is used to execute commands installed with Coopr.',
        epilog="""
This subcommand can execute any command from the bin (or Script)
directory that is created when Coopr is installed.  Note that this
includes any commands that are installed by other Python packages
that are installed with Coopr.  Thus, if Coopr is installed in the
Python system directories, then this command executes any command
included with Python.
"""
        ))
coopr_parser.add_subparser('version',
        func=version_exec, 
        help='Print the Coopr version.',
        description='This coopr subcommand is used to print the version of the Coopr release.')

def main(args=None):
    parser = argparse.ArgumentParser()
    setup_parser(parser)
    parser.set_defaults(func=main_exec)
    ret = parser.parse_args(args)
    ret = ret.func(ret)


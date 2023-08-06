# Copyright (c) 2011-2012, 30loops.net
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of 30loops.net nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL 30loops.net BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
Command line interface for the 30loops platform.
"""

import tempfile
import os
import subprocess
import json
import sys
import argparse
import ConfigParser

from thirtycli import utils
from libthirty import documents
from libthirty.state import env
from libthirty.logbook import LogBookHandler
from libthirty.actions import ActionHandler
from libthirty.resource_manager import ResourceManager
from libthirty.exceptions import HttpReturnError
from docar.exceptions import HttpBackendError


def ascii_art():
    art = """
    _____ _____ _                                    _
   |____ |  _  | |                                  | |
       / / |/' | | ___   ___  _ __  ___   _ __   ___| |_
       \ \  /| | |/ _ \ / _ \| '_ \/ __| | '_ \ / _ \ __|
   .___/ | |_/ / | (_) | (_) | |_) \__ \_| | | |  __/ |_
   \____/ \___/|_|\___/ \___/| .__/|___(_)_| |_|\___|\__|
                             | |
                             |_|
"""
    return art


class CommandError(Exception):
    pass


class CustomArgumentParser(argparse.ArgumentParser):
    """Override the default error method to hint more help to the user."""
    def error(self, message):
        self.print_usage()
        print >> sys.stderr, '\n'
        print >> sys.stderr, 'See "thirty help" for more information.'
        print >> sys.stderr, 'See "thirty help COMMAND" for help on a\
specific command.'
        sys.exit(1)


class ThirtyCommandShell(object):
    """The shell command dispatcher."""
    def get_base_parser(self):
        parser = CustomArgumentParser(
                prog="thirty",
                description=__doc__.strip(),
                epilog='See "thirty help COMMAND" '\
                       'for help on a specific command.',
                add_help=False
                )

        ###
        # Global arguments
        ###

        # Surpress the -h/--help command option
        parser.add_argument('-h', '--help',
            action='help',
            help=argparse.SUPPRESS)

        #parser.add_argument("-d", "--debug",
        #    default=False,
        #    action="store_true",
        #    help="Print debug statements. !! Can be verbose. !!")

        parser.add_argument("-u", "--username",
                action="store",
                metavar="<username>",
                help="The username that should be used for this request.")

        parser.add_argument("-p", "--password",
                action="store",
                metavar="<password>",
                help="The password to use for authenticating this request.")

        parser.add_argument("-a", "--account",
                action="store",
                metavar="<account>",
                help="The account that this user is a member of.")

        parser.add_argument("-r", "--uri",
                action="store",
                metavar="<uri>",
                default="https://api.30loops.net",
                help="Use <uri> as target URI for the 30loops platform.\
Normally you don't need that.")

        parser.add_argument("-i", "--api",
                action="store",
                metavar="<api>",
                default="1.0",
                help="The version of the api to use, defaults to 1.0.")

        parser.add_argument("-R", "--raw",
                action="store_true",
                default=False,
                help="Show the output as raw json.")

        return parser

    def get_subcommand_parsers(self, parser):
        """Populate the subparsers."""
        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar="<subcommand>")

        self._find_subcommands(subparsers, self)

        return parser

    def _find_subcommands(self, subparsers, subcommand_module):
        """Find all subcommand arguments."""
        # load for each subcommands the appropriate shell file
        for attr in (a for a in dir(subcommand_module) if a.startswith('do_')):
            # make the commands have hyphens in place of underscores
            command = attr[3:].replace('_', '-')
            callback = getattr(subcommand_module, attr)
            desc = callback.__doc__ or ''
            help = desc.strip().split('\n')[0]
            arguments = getattr(callback, 'arguments', [])

            subparser = subparsers.add_parser(command,
                    help=help,
                    add_help=False,
                    description=desc)

            subparser.add_argument('-h', '--help',
                action='help',
                help=argparse.SUPPRESS,
            )

            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

    def main(self, argv):
        """Entry point of the command shell."""
        defaults = {}
        # First read out file based configuration
        config = ConfigParser.SafeConfigParser()
        config.read(os.path.expanduser('~/.thirty.cfg'))
        if config.has_section('thirtyloops'):
            defaults = dict(config.items('thirtyloops'))

        parser = self.get_base_parser()

        # set the configfile as defaults
        parser.set_defaults(**defaults)

        subcommand_parser = self.get_subcommand_parsers(parser)
        self.parser = subcommand_parser

        args = subcommand_parser.parse_args(argv)

        # Handle global arguments
        if args.uri:
            env.base_uri = args.uri
        if args.account:
            env.account = args.account
        if args.api:
            env.api_version = args.api

        # Short-circuit and deal with help right away.
        if args.func == self.do_help:
            self.do_help(args)
            return 0

        #args.func(self.cs, args)
        args.func(args)

    @utils.arg('command', metavar='<subcommand>', nargs='?',
                    help='Display help for <subcommand>')
    def do_help(self, args):
        """
        Display help about this program or one of its subcommands.
        """
        if args.command:
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise CommandError("'%s' is not a valid subcommand" %
                                       args.command)
        else:
            print ascii_art()
            self.parser.print_help()

    ##
    # Helper functions
    ##
    def _format_output(self, obj):
        return json.dumps(obj, indent=4)

    def _format_error(self, error):
        return json.dumps(error, indent=4)

    def _get_document(self, label):
        try:
            Document = getattr(documents, label.capitalize())
        except AttributeError:
            sys.stderr.write("Unknown resource label.")
            sys.stderr.flush()

        return Document

    def _poll_logbook(self, uuid):
        import time

        lbh = LogBookHandler(uuid)
        time.sleep(3)
        while True:
            messages = lbh.fetch()
            for msg in messages:
                if msg['loglevel'] == 1:
                    sys.stdout.write(utils.format_logbook_message(msg))
                    sys.stdout.write('\n')
                elif msg['loglevel'] == 3:
                    sys.stderr.write(utils.format_logbook_message(msg))
                    sys.stderr.write('\n')
            if lbh.status in 'finished':
                sys.stdout.write('\n')
                break
            if lbh.status in 'error':
                sys.stderr.write('\n')
                break
            time.sleep(5)

    def _editor(self, scaffold={}):
        """Open an editor and return the edited json text."""
        (fd, path) = tempfile.mkstemp(suffix='_thirty.json', text=True)
        with open(path, 'w+') as f:
            json.dump(scaffold, f, sort_keys=True, indent=4)
            f.flush()
            editor = os.environ['EDITOR']
            process = subprocess.Popen("%s %s" % (editor, path), shell=True)
            process.wait()
            f.seek(0)
            arr = f.readlines()
            arr = [x.strip() for x in arr]

        os.unlink(path)
        os.path.exists(path)

        try:
            obj = json.loads(' '.join(arr))
        except ValueError:
            sys.stderr.write('The input string was not valid.\n')
            sys.stderr.write(' '.join(arr))
            sys.stderr.flush()
            sys.exit(1)

        if obj == scaffold:
            # no changes were made
            sys.stderr.write("The document didn't change. Aborting.\n")
            sys.stderr.flush()
            sys.exit(1)

        return obj

    ##
    # Create resources
    ##
    @utils.arg('label',
            default=None,
            metavar="<label>",
            help="Type of the resource to create.")
    @utils.arg('resource_name',
            default=None,
            metavar="<resource>",
            help="Name of the resource to create.")
    @utils.arg('environment',
            default=None,
            metavar="environment",
            nargs="?",
            help="Create a specific app environment. This option only \
applies for app resources.")
    def do_create(self, args):
        """Create a new resource."""
        if args.raw:
            out = utils.RawOutputFormater()
        else:
            out = utils.ResourceOutputFormater()

        env.label = args.label
        if args.label in 'app' and args.environment:
            env.resource = args.resource_name
            Document = getattr(documents, 'PythonEnvironment')
            context = {'app': args.resource_name}
            name = args.environment
        else:
            Document = self._get_document(args.label)
            context = {}
            name = args.resource_name

        document = Document({'name': name}, context=context)
        obj = self._editor(document.scaffold())

        # overwrite the name in case it has been edited
        obj['name'] = name

        # Create the document again, but this time with the full message
        document = Document(obj, context=context)

        try:
            document.save(username=args.username, password=args.password)
        except HttpBackendError as e:
            # The backend thorws an exception, some error code should have been
            # returned.
            out.error(json.loads(e[1]))
            sys.exit(1)

        out.info(document.to_python())

    ##
    # Show resources
    ##
    @utils.arg('label',
            default=None,
            metavar="<label>",
            help="Type of the resource to create.")
    @utils.arg('resource_name',
            default=None,
            metavar="<resource>",
            help="Name of the resource to create.")
    @utils.arg('environment',
            default=None,
            metavar="environment",
            nargs="?",
            help="Work on a specific app environment. This option only \
applies for app resources."
            )
    def do_show(self, args):
        """Show the details of a resource."""
        if args.raw:
            out = utils.RawOutputFormater()
        else:
            out = utils.ResourceOutputFormater()

        env.label = args.label
        env.resource = args.resource_name
        if args.label in 'app' and args.environment:
            Document = getattr(documents, 'PythonEnvironment')
            document = Document({'name': args.environment},
                    context={'app': args.resource_name})
        else:
            Document = self._get_document(args.label)
            document = Document({'name': args.resource_name})
        try:
            document.fetch(username=args.username, password=args.password)
        except HttpBackendError as e:
            # The backend thorws an exception, some error code should have been
            # returned.
            out.error(json.loads(e[1]))
            sys.exit(1)

        out.info(document.to_python())

    ##
    # Update resources
    ##
    @utils.arg('label',
            default=None,
            metavar="<label>",
            help="Type of the resource to create.")
    @utils.arg('resource_name',
            default=None,
            metavar="<resource>",
            help="Name of the resource to create.")
    @utils.arg('environment',
            default=None,
            metavar="environment",
            nargs="?",
            help="Create a specific app environment. This option only \
applies for app resources."
            )
    def do_update(self, args):
        """Update a resource."""
        if args.raw:
            out = utils.RawOutputFormater()
        else:
            out = utils.ResourceOutputFormater()

        env.label = args.label
        if args.label in 'app' and args.environment:
            env.resource = args.resource_name
            Document = getattr(documents, 'PythonEnvironment')
            document = Document({'name': args.environment},
                    context={'app': args.resource_name})
        else:
            Document = self._get_document(args.label)
            document = Document({'name': args.resource_name})

        #FIXME: if a 404 returns, exit the client, no update possible
        try:
            document.fetch(username=args.username, password=args.password)
        except HttpBackendError as e:
            # The backend throws an exception, some error code should have been
            # returned.
            out.error(json.loads(e[1]))
            sys.exit(1)

        try:
            obj = self._editor(document._prepare_render())
            document.update(obj,
                    username=args.username, password=args.password)
        except HttpBackendError as e:
            # The backend throws an exception, some error code should have been
            # returned.
            out.error(json.loads(e[1]))
            sys.exit(1)

    ##
    # Delete resources
    ##
    @utils.arg('label',
            default=None,
            metavar="<label>",
            help="Type of the resource to create.")
    @utils.arg('resource_name',
            default=None,
            metavar="<resource>",
            help="Name of the resource to create.")
    @utils.arg('environment',
            default=None,
            metavar="environment",
            nargs="?",
            help="Work on a specific app environment. This option only \
applies for app resources."
            )
    def do_delete(self, args):
        """Delete a resource."""
        if args.raw:
            out = utils.RawOutputFormater()
        else:
            out = utils.ResourceOutputFormater()

        env.label = args.label
        if args.label in 'app' and args.environment:
            env.resource = args.resource_name
            Document = getattr(documents, 'PythonEnvironment')
            document = Document({'name': args.environment},
                    context={'app': args.resource_name})
        else:
            Document = self._get_document(args.label)
            document = Document({'name': args.resource_name})
        try:
            document.delete(username=args.username, password=args.password)
        except HttpBackendError as e:
            # The backend thorws an exception, some error code should have been
            # returned.
            out.error(json.loads(e[1]))
            sys.exit(1)

    ##
    # List resources
    ##
    @utils.arg('label',
            default=None,
            metavar="<label>",
            help="Type of the resource to create.")
    def do_list(self, args):
        """List all resources of a type."""
        env.username = args.username
        env.password = args.password
        env.account = args.account
        env.label = args.label

        if args.raw:
            out = utils.RawOutputFormater()
        else:
            out = utils.ResourceOutputFormater()

        rm = ResourceManager()
        rm.list()
        out.info(rm.content)

    ##
    # View logbook
    ##
    @utils.arg('uuid',
            default=None,
            metavar="<uuid>",
            help="The UUID of the logbook.")
    def do_logbook(self, args):
        """Poll the logbook for an action."""
        env.username = args.username
        env.password = args.password

        lbh = LogBookHandler(args.uuid)
        try:
            lbh.fetch()
        except HttpReturnError as e:
            #FIXME: push this into its own formatting method
            error = {
                    "code": e[0],
                    "message": e[1]
                    }
            sys.stderr.write(json.dumps(error, indent=4))
            sys.stderr.flush()
            sys.exit(1)

        if args.raw:
            sys.stdout.write(lbh.response.content)
        else:
            sys.stdout.write(self._format_output(
                json.loads(lbh.response.content)))

    ##
    # Deploy app resources
    ##
    @utils.arg('resource_name',
            default=None,
            metavar="<resource>",
            help="The name of the resource to create.")
    @utils.arg('environment',
            default='production',
            metavar="<environment>",
            help="The name of the environment to deploy.")
    def do_deploy(self, args):
        """Deploy an app resource."""
        cmd = {'action': 'deploy', 'options': {}}
        cmd['options']['environment'] = args.environment

        env.account = args.account
        env.label = 'app'
        env.resource = args.resource_name
        env.username = args.username
        env.password = args.password

        action = ActionHandler(**cmd)

        try:
            # Lets queue the action
            action.queue()
        except HttpReturnError as e:
            #FIXME: push this into its own formatting method
            error = {
                    "code": e[0],
                    "message": e[1]
                    }
            sys.stderr.write(json.dumps(error, indent=4))
            sys.stderr.flush()
            sys.exit(1)

        if action.response.status_code >= 500:
            sys.stderr.write(action.response.content)
            sys.stderr.flush()
            sys.exit(1)

        else:
            ret = {
                    'code': action.response.status_code,
                    'message': action.response.content,
                    'logbook': action.response.headers['Location']
                }

        if args.raw:
            # we dont poll the logbook in raw mode.
            sys.stdout.write(json.dumps(ret))
            sys.stdout.flush()
            return

        try:
            self._poll_logbook(action.uuid)
        except KeyboardInterrupt:
            sys.exit(1)
        except HttpReturnError as e:
            #FIXME: push this into its own formatting method
            error = {
                    "code": e[0],
                    "message": e[1]
                    }
            sys.stderr.write(json.dumps(error, indent=4))
            sys.stderr.flush()
            sys.exit(1)

        sys.stdout.flush()

    ##
    # run a django command
    ##
    @utils.arg('resource_name',
            default=None,
            metavar="<resource>",
            help="Name of the app.")
    @utils.arg('environment',
            default='production',
            metavar="<environment>",
            help="The name of the environment.")
    @utils.arg('command',
            default=None,
            metavar="<command>",
            help="The django management command to run on the remote server.")
    @utils.arg('--occurence',
            default=1,
            help="The number of instance to run the command on or all.",
            type=utils.occurence)
    def do_djangocmd(self, args):
        """Run a django management command."""
        cmd = {'action': 'djangocommand', 'options': {}}
        cmd['options']['environment'] = args.environment
        cmd['options']['command'] = args.command
        cmd['options']['occurence'] = args.occurence

        env.account = args.account
        env.label = 'app'
        env.resource = args.resource_name
        env.username = args.username
        env.password = args.password

        action = ActionHandler(**cmd)

        try:
            # Lets queue the action
            action.queue()
        except HttpReturnError as e:
            #FIXME: push this into its own formatting method
            error = {
                    "code": e[0],
                    "message": e[1]
                    }
            sys.stderr.write(json.dumps(error, indent=4))
            sys.stderr.flush()
            sys.exit(1)

        if action.response.status_code >= 500:
            sys.stderr.write(action.response.content)
            sys.stderr.flush()
            sys.exit(1)

        else:
            ret = {
                    'code': action.response.status_code,
                    'message': action.response.content,
                    'logbook': action.response.headers['Location']
                }

        if args.raw:
            # we dont poll the logbook in raw mode.
            sys.stdout.write(json.dumps(ret))
            sys.stdout.flush()
            return

        try:
            self._poll_logbook(action.uuid)
        except KeyboardInterrupt:
            sys.exit(1)
        except HttpReturnError as e:
            #FIXME: push this into its own formatting method
            error = {
                    "code": e[0],
                    "message": e[1]
                    }
            sys.stderr.write(json.dumps(error, indent=4))
            sys.stderr.flush()
            sys.exit(1)

        sys.stdout.flush()

    ##
    # run a generic command
    ##
    @utils.arg('resource_name',
            default=None,
            metavar="<resource>",
            help="Name of the app.")
    @utils.arg('environment',
            default='production',
            metavar="<environment>",
            help="The name of the environment.")
    @utils.arg('command',
            default=None,
            metavar="<command>",
            help="The command to run on the remote server.")
    @utils.arg('--occurence',
            default=1,
            help="The number of instance to run the command on or all.",
            type=utils.occurence)
    def do_runcmd(self, args):
        """Run a generic command."""
        cmd = {'action': 'runcommand', 'options': {}}
        cmd['options']['environment'] = args.environment
        cmd['options']['command'] = args.command
        cmd['options']['occurence'] = args.occurence

        env.account = args.account
        env.label = 'app'
        env.resource = args.resource_name
        env.username = args.username
        env.password = args.password

        action = ActionHandler(**cmd)

        try:
            # Lets queue the action
            action.queue()
        except HttpReturnError as e:
            #FIXME: push this into its own formatting method
            error = {
                    "code": e[0],
                    "message": e[1]
                    }
            sys.stderr.write(json.dumps(error, indent=4))
            sys.stderr.flush()
            sys.exit(1)

        if action.response.status_code >= 500:
            sys.stderr.write(action.response.content)
            sys.stderr.flush()
            sys.exit(1)

        else:
            ret = {
                    'code': action.response.status_code,
                    'message': action.response.content,
                    'logbook': action.response.headers['Location']
                }

        if args.raw:
            # we dont poll the logbook in raw mode.
            sys.stdout.write(json.dumps(ret))
            sys.stdout.flush()
            return

        try:
            self._poll_logbook(action.uuid)
        except KeyboardInterrupt:
            sys.exit(1)
        except HttpReturnError as e:
            #FIXME: push this into its own formatting method
            error = {
                    "code": e[0],
                    "message": e[1]
                    }
            sys.stderr.write(json.dumps(error, indent=4))
            sys.stderr.flush()
            sys.exit(1)

        sys.stdout.flush()


def main():
    try:
        ThirtyCommandShell().main(sys.argv[1:])
    except Exception, e:
        print >> sys.stderr, e
        sys.exit(1)

import sys
import json

from thirtycli import utils
from thirtycli.actions.common import Action
from libthirty.state import env
from docar.exceptions import HttpBackendError

class ShowAction(Action):
    """Show a resource"""
    ##
    # Show resources
    ##

    @utils.arg('type',
        default=None,
        choices=["app", "environment", "repository"],
        help="Type to show")
    @utils.arg('name',
        default=None,
        help="Name of the type to show")
    @utils.arg('--environment',
        '--env',
        default=None,
        nargs='?',
        help="Name of the environment")
    def show(self, args):
        """Show the details of a resource"""
        if args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        env.label = args.type
        env.resource = args.name

        if args.type in "environment" and not (args.name and args.environment):
            sys.stderr.write("Please provide both an application name and \
environment name")
            sys.exit(1)

        if args.environment:
            Document = utils._get_document('PythonEnvironment')
            document = Document({'name': args.environment},
                        context={'app': args.name})
        else:
            Document = utils._get_document(args.type.capitalize())
            document = Document({'name': args.name})

        try:
            document.fetch(username=args.username, password=args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        out.info(document._to_dict())

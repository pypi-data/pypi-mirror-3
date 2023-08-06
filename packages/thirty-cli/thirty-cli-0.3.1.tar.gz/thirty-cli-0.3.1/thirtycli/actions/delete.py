import sys
import json

from thirtycli.actions.common import Action
from thirtycli import utils
from libthirty.state import env
from docar.exceptions import HttpBackendError

class DeleteAction(Action):
    """Delete a resource"""

    @utils.arg('name',
        default=None,
        help="Name of the app to delete.")
    def app(self, args):
        """Delete an app"""
        if args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        env.label = args.func.__name__

        Document = utils._get_document(env.label.capitalize())
        document = Document({'name': args.name})

        try:
            document.delete(username=args.username, password=args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

    @utils.arg('name',
        default=None,
        help="Name of the repository to delete.")
    def repository(self, args):
        """Delete a repository"""
        if args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        env.label = args.func.__name__

        Document = utils._get_document(env.label.capitalize())
        document = Document({'name': args.name})

        try:
            document.delete(username=args.username, password=args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        if not args.raw:
            out.info("--> Repository %s is deleted" % args.name)

    @utils.arg('app',
        default=None,
        help="Name of the app to delete the environment from.")
    @utils.arg('environment',
        help="Name of the environment to delete")
    def environment(self, args):
        """Delete an environment"""
        if args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        env.label = args.func.__name__
        env.resource = args.app

        Environment = utils._get_document('PythonEnvironment')
        environment = Environment({'name': args.environment})

        try:
            environment.delete(username=args.username, password=args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        if not args.raw:
            out.info("--> Environment %s is deleted from app %s" % (
                args.environment, args.app))

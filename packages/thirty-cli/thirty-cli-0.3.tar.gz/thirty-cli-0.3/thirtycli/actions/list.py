from thirtycli import utils
from thirtycli.actions.common import Action
from libthirty.state import env
from libthirty.resource_manager import ResourceManager


class ListAction(Action):
    """List resources"""
    ##
    # List resources
    ##
    @utils.arg('type',
           default="app",
           choices=["app", "repository"],
           help="Type of the resource(s)")
    def list(self, args):
        """List all resources of a type."""
        env.label = args.type
        env.username = args.username
        env.password = args.password
        env.account = args.account

        rm = ResourceManager()
        rm.list()

        if args.raw:
            out = utils.RawOutputFormatter()
            out.info(rm.content)
        else:
            out = utils.ResourceOutputFormatter()
            for item in rm.content['items']:
                out.info(item['name'])

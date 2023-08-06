from thirtycli.actions.common import Action
from thirtycli import utils

class ShowAction(Action):
    """Show the details of an app."""

    RESOURCE_COMMAND = True

    ##
    # Show resources
    ##
    @utils.arg('resource',
            metavar="<app>",
            help="The resource to show.")
    def do_show(self, args, global_args):
        """Show the details of an app."""

        self._show_resource(args, global_args)

import json
import sys

from thirtycli import utils
from thirtycli.actions.common import Action
from libthirty.state import env
from libthirty.logbook import LogBookHandler
from libthirty.exceptions import HttpReturnError


class LogbookAction(Action):
    """View the actions logbook"""
    ##
    # View logbook
    ##
    @utils.arg('uuid',
            default=None,
            metavar="<uuid>",
            help="The UUID of the logbook.")
    def logbook(self, args):
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
            sys.stdout.write(utils._format_output(
                json.loads(lbh.response.content)))

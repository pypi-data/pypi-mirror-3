import json
import sys

from thirtycli import utils
from thirtycli.actions.common import Action
from libthirty.state import env
from libthirty.logs import LogsHandler
from libthirty.exceptions import HttpReturnError


class LogsAction(Action):
    """View the logs of your application"""
    @utils.arg('name',
            default=None,
            metavar="<name>",
            help="Name of the application")
    @utils.arg('--environment',
            '--env',
            default="production",
            help="Name of the default environment")
    @utils.arg('--process',
            default=None,
            nargs='*',
            help=("Specify the process to get the logs from " +
                "(default: gunicorn,nginx)"))
    @utils.arg('--limit',
            default=None,
            help="The number of entries to return (default: 10)")
    def logs(self, args):
        """View the logs of your application"""
        env.username = args.username
        env.password = args.password

        params = {}
        if args.process:
            params['process'] = args.process
        if args.limit:
            params['limit'] = args.limit

        logs = LogsHandler(
                args.name,
                args.environment,
                **params)
        try:
            logs.fetch()
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
            sys.stdout.write(logs.response.content)
        else:
            sys.stdout.write(utils._format_logoutput(
               json.loads(logs.response.content)))

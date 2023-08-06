import sys
import json

from thirtycli.actions.common import Action
from thirtycli import utils
from libthirty.state import env
from libthirty.actions import ActionHandler
from libthirty.exceptions import HttpReturnError

class DjangocmdAction(Action):
    """Run a Django command"""
    ##
    # run a generic command
    ##
    @utils.arg('app',
            default=None,
            metavar="<app>",
            help="Name of the app")
    @utils.arg('command',
            default=None,
            nargs='*',
            metavar="<command>",
            help="Command to run")
    @utils.arg('--environment',
            '--env',
            default='production',
            metavar="<environment>",
            help="Name of the environment (default: production)")
    @utils.arg('--occurence',
            default=1,
            help="Number of instances to run the command on (use \"all\" for \
all instances)",
            type=utils.occurence)
    def djangocmd(self, args):
        """Run a Django command"""
        cmd = {'action': 'djangocommand', 'options': {}}
        cmd['options']['environment'] = args.environment
        cmd['options']['command'] = " ".join(args.command)
        cmd['options']['occurence'] = args.occurence

        env.account = args.account
        env.label = 'app'
        env.resource = args.app
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
            utils._poll_logbook(action.uuid)
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


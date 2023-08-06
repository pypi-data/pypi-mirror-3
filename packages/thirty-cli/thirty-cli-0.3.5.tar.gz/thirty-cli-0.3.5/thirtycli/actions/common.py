from docar.exceptions import HttpBackendError, BackendDoesNotExist
from thirtycli.utils import confirm
from thirtycli import utils
from libthirty.state import env
from argparse import SUPPRESS
from libthirty.exceptions import HttpReturnError
from libthirty.actions import ActionHandler

import sys
import json


class Action(object):
    @classmethod
    def map_app_name(cls, resource, parser):
        """Map the appname to the app action and set it as a parser option."""
        if len(resource) < 1:
            # Some input is missins obviously, so we just return here, and let
            # argparse handle the situation
            return resource
        command = resource[0].split('.')

        if len(command) < 2:
            resource[0] = 'app'
            # We do this so that we can easily set the label below
            command.append('app')
        else:
            resource[0] = 'app.%s' % command[1]

        # Add the app name as an argument
        parser.add_argument('appname',
                action='store',
                help=SUPPRESS,
                default=command[0])

        # Add the resource label as an argument
        parser.add_argument('label',
                action='store',
                help=SUPPRESS,
                default=command[1])

        # Append the actual appname to the argument input, the appname argument
        # has been added last to the parser, therefore we append it to the
        # list.
        resource.append(command[0])
        resource.append(command[1])

        return resource

    def _output_formatter(self, global_args):
        """Configure the output formatter."""
        if global_args.raw:
            self.out = utils.RawOutputFormatter()
        else:
            self.out = utils.ResourceOutputFormatter()

    def _create_resource(self, args, global_args, resource):
        """Create a resource"""
        self._output_formatter(global_args)

        try:
            resource.save(username=env.username, password=env.password)
        except HttpBackendError as e:
            self.out.error(json.loads(e[1]))
            sys.exit(1)

        if global_args.raw:
            self.out.info(resource.to_python())
        else:
            self.out.info("--> %s %s is created!" % (args.label.capitalize(),
                args.appname))
            self.out.info("--> Details of the %s:\n" % args.label)
            args.type = args.label
            self._show_resource(args, global_args)
            if args.label == 'app':
                self.out.info("\n--> You can now deploy the %s with: thirty deploy %s" % (
                args.label, args.appname))

    def _update_resource(self, args, global_args, resource):
        """Update a resource with an additional resource"""
        self._output_formatter(global_args)

        try:
            resource.save(username=env.username, password=env.password)
        except HttpBackendError as e:
            self.out.error(json.loads(e[1]))
            sys.exit(1)

        if global_args.raw:
            self.out.info(resource.to_python())
        else:
            self.out.info("--> %s %s is created!" % (args.label.capitalize(), args.appname))
            self.out.info("--> Details of the %s:\n" % args.label)
            args.type = args.label
            self._show_resource(args, global_args)

    def _show_resource(self, args, global_args):
        """Show the details of a resource."""
        self._output_formatter(global_args)

        App = utils._get_document('App')
        app = App({'name': args.appname})

        try:
            app.fetch(username=env.username, password=env.password)
        except (BackendDoesNotExist, HttpBackendError) as e:
            self.out.error(json.loads(e[1]))
            sys.exit(1)

        if args.label == 'app':
            document = app
        else:
            document = getattr(app, args.label)

        if document:
            self.out.info(document._to_dict())
        else:
            self.out.info("%s %s does not exist" % (args.label.capitalize(), args.appname))

    def _delete_resource(self, args, global_args):
        """Delete a resource."""
        self._output_formatter(global_args)

        env.label = args.label

        App = utils._get_document('App')
        app = App({'name': args.appname})

        try:
            app.fetch(username=env.username, password=env.password)
        except HttpBackendError as e:
            self.out.error(json.loads(e[1]))
            sys.exit(1)

        if args.label == 'app':
            document = app
            prompt = 'Do you really want to delete %s %s?' % (
                    args.label, args.appname)
        else:
            if not getattr(app, args.label):
                self.out.info("App %s has no %s." % (args.appname, args.label))
                sys.exit(1)
            document = getattr(app, args.label)
            prompt = 'Do you really want to delete the %s of app %s?' % (
                    args.label, args.appname)

        resp = confirm(prompt=prompt, resp=False)

        if resp == False:
            if not global_args.raw:
                self.out.info("Delete aborted.")
            sys.exit(1)

        try:
            document.delete(username=env.username, password=env.password)
        except HttpBackendError as e:
            self.out.error(json.loads(e[1]))
            sys.exit(1)

        if not global_args.raw:
            self.out.info("%s %s is deleted!" % (args.label.capitalize(), args.appname))


    def _run_command(self, args, global_args, cmd):
        """Run an arbitrary command"""

        self._output_formatter(global_args)

        env.label = args.label
        env.resource = args.appname

        action = ActionHandler(**cmd)

        try:
            # Lets queue the action
            action.queue()
        except HttpReturnError as e:
            self.out.error(e[1])
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

        if global_args.raw:
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

    def _show_usage(self, args, global_args):
        """Show the details of a resource."""
        self._output_formatter(global_args)

        App = utils._get_document('App')
        app = App({'name': args.appname})

        try:
            app.fetch(username=env.username, password=env.password)
        except HttpBackendError as e:
            self.out.error(json.loads(e[1]))
            sys.exit(1)

        if args.label == 'app':
            document = app
        else:
            document = getattr(app, args.label)

        if document:
            self.out.info(document._to_dict())
        else:
            self.out.info("%s %s does not exist" % (args.label.capitalize(), args.appname))

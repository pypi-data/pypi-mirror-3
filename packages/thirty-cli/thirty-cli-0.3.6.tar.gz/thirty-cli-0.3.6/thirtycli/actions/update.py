import sys
import json
import base64

from thirtycli import utils
from thirtycli.actions.common import Action
from thirtycli.actions.show import ShowAction
from libthirty.state import env
from docar.exceptions import HttpBackendError

class UpdateAction(Action):
    """Update the configuration of a resource."""
    positional = 'resource'
    RESOURCE_COMMAND = True

    ##
    # Update an application
    ##
    @utils.arg('--add-cname',
            default=None,
            action="append",
            help="Add an additional CNAME to the app.")
    @utils.arg('--del-cname',
            default=None,
            action="append",
            help="Remove a CNAME from the app.")
    @utils.arg('--instances',
            default=1,
            type=int,
            help="The number of instances to deploy your app on.")
    @utils.arg('--repository',
            default=None,
            help="Change the repository to use for this app.")
    @utils.arg('--repo-commit',
            default=None,
            help="Commit or branch of the repository to clone.")
    def do_app(self, args, global_args):
        """Update the configuration of an app."""
        if global_args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        env.label = args.label
        env.resource = args.appname

        App = utils._get_document("App")
        app = App({'name': args.appname})

        try:
            app.fetch(username=global_args.username, password=global_args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        if args.instances:
            app.instances = args.instances

        if args.add_cname:
            Cname = utils._get_document('CnameRecord')
            for c in args.add_cname:
                cname = Cname({'record': c})
                app.cnames.add(cname)

        if args.del_cname:
            for c in args.del_cname:
                app.cnames.delete({'record': c})

        if args.repo_commit:
            app.repo_commit = args.repo_commit

        if args.repository:
            app.repository.name = args.repository

        try:
            app.save(username=global_args.username, password=global_args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        if global_args.raw:
            out.info(app.to_python())
        else:
            out.info("--> %s %s updated!" % (env.label.capitalize(), args.appname))
            out.info("--> New %s configuration:\n" % env.label)
            output = ShowAction()
            output.do_show(args, global_args)

    ##
    # Update a repository
    ##
    @utils.arg('--name',
            default=None,
            metavar='<repository>',
            help=("Name of the repository to update (if not specified, "
                "<app>.repository will be used"))
    @utils.arg('--location',
            default=None,
            help="URI of the repository.")
    @utils.arg('--ssh-key',
            default=None,
            help="SSH key for a non-public repository (specify full path).")
    def do_app_repository(self, args, global_args):
        """Update the configuration of a repository."""
        if global_args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        context = {}

        env.label = args.label

        Repository = utils._get_document("Repository")

        if args.name:
            repository = Repository({'name': args.name}, context=context)
        else:
            repository = Repository({'name': args.appname}, context=context)

        try:
            repository.fetch(username=global_args.username, password=global_args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        if args.location:
            repository.location = args.location

        if args.ssh_key:
            with open(args.ssh_key, 'r') as f:
                repository.ssh_key = base64.b64encode(f.read())

        try:
            repository.save(username=global_args.username, password=global_args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        if global_args.raw:
            out.info(repository.to_python())
        else:
            out.info("--> %s %s updated!" % (args.label.capitalize(), repository.name))
            out.info("--> New %s configuration:\n" % args.label)
            output = ShowAction()
            output.do_show(args, global_args)


    @utils.arg('--instances',
            required=True,
            default=1,
            type=int,
            help="The number of worker instances to deploy.")
    def do_app_worker(self, args, global_args):
        """Update the configuration of a worker."""
        if global_args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        env.label = args.label
        env.resource = args.appname

        Worker = utils._get_document("Worker")
        worker = Worker({'name': args.appname})

        try:
            worker.fetch(username=global_args.username, password=global_args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        worker.instances = args.instances

        try:
            worker.save(username=global_args.username, password=global_args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        if global_args.raw:
            out.info(worker.to_python())
        else:
            out.info("--> %s %s updated!" % (args.label.capitalize(), args.appname))
            out.info("--> New %s configuration:\n" % args.label)
            output = ShowAction()
            output.do_show(args, global_args)


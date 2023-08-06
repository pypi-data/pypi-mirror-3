import sys
import json
import base64

from thirtycli import utils
from thirtycli.actions.common import Action
from docar.exceptions import HttpBackendError


class CreateAction(Action):
    """Create a new resource."""
    positional = 'resource'

    RESOURCE_COMMAND = True

    #     return resource
    ##
    # Create an application
    ##
    @utils.arg('location',
            metavar="<location>",
            help="This is the URI of the repository that will be used for this app.")
    @utils.arg('--cname',
            default=None,
            action="append",
            help="Connect a CNAME record to this app. Specify multiple times if needed.")
    @utils.arg('--repository',
            default=None,
            help="Specify an existing repository to connect to this app.")
    @utils.arg('--region',
            default='ams1',
            help="The region of this app (defaults to ams1).")
    @utils.arg('--instances',
            default=1,
            type=int,
            help="The number of instances to deploy your app on.")
    @utils.arg('--no-db',
            default=True,
            action='store_false',
            help='Don\'t create a database for this app.')
    @utils.arg('--variant',
            default='python',
            help="The variant of this app (default: python).")
    def do_app(self, args, global_args):
        """Create a new app."""
        if global_args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        App = utils._get_document("App")
        app = App({'name': args.appname})

        app.instances = args.instances

        if args.cname:
            Cname = utils._get_document('CnameRecord')
            for c in args.cname:
                cname = Cname({'record': c})
                app.cnames.add(cname)

        if args.repository:
            Repository = utils._get_document('Repository')
            repository = Repository({'name': args.repository})
            try:
                repository.fetch(username=global_args.username, password=global_args.password)
            except HttpBackendError as e:
                out.error(json.loads(e[1]))
                sys.exit(1)
            app.repository = repository
        else:
            if args.location:
                app.repository.location = args.location
                app.repository.variant = "git"
                app.repository.name = args.appname
            else:
                sys.stderr.write("You have to specify a location or an existing repository")
                sys.exit(1)

        # Create a database resource if necessary
        if args.no_db and args.variant not in "static":
            Database = utils._get_document('Database')
            db = Database({'name': args.appname},
                    context={'account': global_args.account})
            app.database = db

        if args.region:
            app.region = args.region

        if args.variant:
            app.variant = args.variant

        self._create_resource(args, global_args, app)

    ##
    # Create a repository
    ##
    @utils.arg('location',
            default=None,
            metavar="<location>",
            help="URI of the repository.")
    @utils.arg('--name',
            default=None,
            metavar="<name>",
            help=("Custom name of the repository resource (will be generated "
            "automatically from the repository URI otherwise)."))
    @utils.arg('--ssh-key',
            default=None,
            help="SSH key (password-less) for a SSH protected repository.")
    def do_app_repository(self, args, global_args):
        """Create a new repository."""
        if global_args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        App = utils._get_document("App")
        app = App({'name': args.appname})

        try:
            app.fetch(username=global_args.username, password=global_args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        if not args.name:
            if args.location:
                args.name = args.location.split("/")[-1].split(".")[0]
            else:
                out.error("Specify either a name or a repository, otherwise we don't know how to name your app!")

        Repository = utils._get_document(args.label.capitalize())
        repository = Repository({'name': args.name})
        repository.location = args.location

        if args.ssh_key:
            with open(args.ssh_key, 'r') as f:
                repository.ssh_key = base64.b64encode(f.read())

        app.repository = repository
        self._update_resource(args, global_args, app)
#        self._create_resource(args, global_args, repository)

    ##
    # Create a worker
    ##
    @utils.arg('--instances',
            default=1,
            help="The number of worker instances to deploy.")
    def do_app_worker(self, args, global_args):
        """Create a new worker."""
        if global_args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        App = utils._get_document("App")
        app = App({'name': args.appname})

        try:
            app.fetch(username=global_args.username, password=global_args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        Worker = utils._get_document("Worker")
        worker = Worker({'name': args.appname})
        worker.region = app.region

        if args.instances:
            worker.instances = args.instances

        app.worker = worker
        self._update_resource(args, global_args, app)

    ##
    # Create a mongodb
    ##
    def do_app_mongodb(self, args, global_args):
        """Create a new mongodb database."""
        if global_args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        App = utils._get_document("App")
        app = App({'name': args.appname})

        try:
            app.fetch(username=global_args.username, password=global_args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        Mongodb = utils._get_document(args.label.capitalize())
        mongodb = Mongodb({'name': args.appname})

        app.mongodb = mongodb
        self._update_resource(args, global_args, app)

    ##
    # Create a mongodb
    ##
    def do_app_database(self, args, global_args):
        """Create a new database."""
        if global_args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        App = utils._get_document("App")
        app = App({'name': args.appname})

        try:
            app.fetch(username=global_args.username, password=global_args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        Database = utils._get_document(args.label.capitalize())
        database = Database({'name': args.appname})

        app.database = database
        self._update_resource(args, global_args, app)

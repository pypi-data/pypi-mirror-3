import sys
import json
import base64

from thirtycli import utils
from thirtycli.actions.common import Action
from libthirty.state import env
from docar.exceptions import HttpBackendError

class UpdateAction(Action):
    """Update a resource or environment"""

    ##
    # Update an application
    ##
    @utils.arg('app',
            default=None,
            metavar='<app>',
            help="Name of the application")
    @utils.arg('--repository',
            '--repo',
            required=True,
            help="Change the repository to use for this app")
    def app(self, args):
        """Update an application"""
        if args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        env.label = args.func.__name__
        env.resource = args.app

        App = utils._get_document("App")
        app = App({'name': args.app})

        try:
            app.fetch(username=args.username, password=args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        app.repository.name = args.repository

        try:
            app.save(username=args.username, password=args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        if args.raw:
            out.info(app.to_python())
        else:
            sys.stdout.write("%s %s updated!" % (env.label.capitalize(), args.app))

    ##
    # Update a repository
    ##
    @utils.arg('repository',
            default=None,
            metavar='<repository>',
            help="Name of the repository")
    @utils.arg('--location',
            required=True,
            help="URL of the repository")
    @utils.arg('--key',
            default=None,
            help="SSH key for a non-public repository (specify full path)")
    @utils.arg('--variant',
            default=None,
            choices=["git"],
            nargs="?",
            help="Variant of the repository")
    def repository(self, args):
        """Update an existing repository"""
        if args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        context = {}

        env.label = args.func.__name__

        Repository = utils._get_document("Repository")
        repository = Repository({'name': args.repository}, context=context)

        try:
            repository.fetch(username=args.username, password=args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        repository.location = args.location

        if args.variant:
            repository.variant = args.variant

        if args.key:
            with open(args.key, 'r') as f:
                repository.ssh_key = base64.b64encode(f.read())

        try:
            repository.save(username=args.username, password=args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        if args.raw:
            out.info(repository.to_python())
        else:
            sys.stdout.write("%s %s updated!" % (env.label.capitalize(), args.repository))

    ##
    # Update an environment
    ##
    @utils.arg('app',
            default=None,
            metavar='<app>',
            help="Name of the app")
    @utils.arg('--environment',
            '--env',
            default="production",
            metavar='<environment>',
            nargs='?',
            help="Name of the environment (default: production)")
    @utils.arg('--add-cname',
            default=None,
            action="append",
            help="Add an additional CNAME to the environment")
    @utils.arg('--del-cname',
            default=None,
            action="append",
            help="Remove a CNAME from the environment")
    @utils.arg('--backends',
            default=None,
            help="Number of backends for this environment")
    @utils.arg('--root',
            default=None,
            help='Root directory of the application')
    @utils.arg('--repo-branch',
            default=None,
            help="Branch of the repository to clone")
    @utils.arg('--repo-commit',
            default=None,
            help="Commit of the repository to clone")
    @utils.arg('--requirements',
            default=None,
            help="Requirements to install")
    @utils.arg('--inject-db',
            default=None,
            choices=['true', 'false'],
            help="Inject database settings into the settings file")
    @utils.arg("--install-setup-py",
            default=None,
            choices=['true', 'false'],
            help="Run setup.py after the deployment")
    @utils.arg('--django-settings-module',
            default=None,
            help='Django settings module')
    @utils.arg('--wsgi-entrypoint',
            default=None,
            help='Entrypoint of the application')
    def environment(self, args):
        """Update an environment of an existing app"""
        if len(sys.argv) < 6:
            sys.stderr.write("Error: no arguments provided")
            sys.exit(1)

        if args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        env.label = "app"
        env.resource = args.app

        Environment = utils._get_document('PythonEnvironment')
        environment = Environment({'name': args.environment})

        try:
            environment.fetch(username=args.username, password=args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        if args.backends is not None:
            Backend = utils._get_document('Backend')
            backend = Backend({'region': 'eu1', 'count': int(args.backends)})
            environment.backends.add(backend)

        if args.add_cname is not None:
            Cname = utils._get_document('CnameRecord')
            for c in args.add_cname:
                cname = Cname({'record': c})
                environment.cname_records.add(cname)

        if args.del_cname is not None:
            for c in args.del_cname:
                environment.cname_records.delete({'record': c})


        flavor = getattr(environment, "%sflavor" % environment.flavor)

        if args.root is not None:
            environment.project_root = args.root
        if args.inject_db is not None:
            flavor.inject_db = args.inject_db.capitalize()
        for key, value in args.__dict__.iteritems():
            if key.startswith(environment.flavor) and value is not None:
                setattr(flavor, key, value)

        if args.requirements is not None:
            environment.requirements_file = args.requirements
        if args.repo_branch is not None:
            environment.repo_branch = args.repo_branch
        if args.repo_commit is not None:
            environment.repo_commit = args.repo_commit
        if args.install_setup_py is not None:
            environment.install_setup_py = args.install_setup_py

        try:
            environment.save(username=args.username, password=args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        if args.raw:
            out.info(environment.to_python())
        else:
            sys.stdout.write("Environment %s of app %s is updated!" % (
                args.environment,
                args.app))


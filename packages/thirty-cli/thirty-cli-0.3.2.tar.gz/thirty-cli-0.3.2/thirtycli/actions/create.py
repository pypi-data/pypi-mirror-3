import sys
import json
import base64

from thirtycli import utils
from thirtycli.actions.common import Action
from libthirty.state import env
from docar.exceptions import HttpBackendError
from thirtycli.actions.show import ShowAction

class CreateAction(Action):
    """Create a new resource or environment"""

    ##
    # Create an application
    ##
    @utils.arg('name',
            default=None,
            metavar="<name>",
            help="Name of the new resource")
    @utils.arg('location',
            default=None,
            nargs='?',
            metavar="<location>",
            help="URL of the repository")
    @utils.arg('--cname',
            default=None,
            action="append",
            help="Comma separated list of cnames")
    @utils.arg('--root',
            default="",
            help='Root directory of the application')
    @utils.arg('--environment',
            '--env',
            default="production",
            help="Name of the default environment")
    @utils.arg('--repository',
            '--repo',
            default=None,
            help="Specify an existing repository resource")
    @utils.arg('--backends',
            default=1,
            help="The number of backends to deploy on")
    @utils.arg('--flavor',
            default=None,
            choices=['django', 'wsgi'],
            required=True,
            help="The flavor of the app.")
    @utils.arg('--requirements',
            default="requirements.txt",
            help="Requirements to install")
    @utils.arg('--install-setup-py',
            default=None,
            choices=['true', 'false'],
            help="Run setup.py during the deployment")
    @utils.arg('--inject-db',
            default=None,
            choices=['true', 'false'],
            help="Inject database settings into the settings file")
    @utils.arg('--django-settings-module',
            default="settings",
            help='Django settings module')
    @utils.arg('--wsgi-entrypoint',
            help='Entrypoint of the application')
    def app(self, args):
        """Create a new application"""
        if args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        env.label = args.func.__name__

        App = utils._get_document("App")
        app = App({'name': args.name})

        Environment = utils._get_document('PythonEnvironment')
        environment = Environment({'name': args.environment})
        environment.requirements_file = args.requirements

        Backend = utils._get_document("Backend")
        backend = Backend({'region': "eu1", "count": int(args.backends)})
        environment.backends.add(backend)

        if args.root:
            environment.project_root = args.root

        if args.cname:
            Cname = utils._get_document('CnameRecord')
            for c in args.cname:
                cname = Cname({'record': c})
                environment.cname_records.add(cname)

        if args.flavor:
            environment.flavor = args.flavor
            flavor = getattr(environment, "%sflavor" % args.flavor)
            flavor.bound = True

            if args.inject_db:
                flavor.inject_db = args.inject_db.capitalize()

            for key, value in args.__dict__.iteritems():
                if key.startswith(args.flavor):
                    setattr(flavor, key, value)

        if args.install_setup_py:
            environment.install_setup_py = args.install_setup_py

        if args.repository:
            Repository = utils._get_document('Repository')
            repository = Repository({'name': args.repository})
            try:
                repository.fetch(username=args.username, password=args.password)
            except HttpBackendError as e:
                out.error(json.loads(e[1]))
                sys.exit(1)
            app.repository = repository
        else:
            if args.location:
                app.repository.location = args.location
                app.repository.variant = "git"
                app.repository.name = args.name
            else:
                sys.stderr.write("You have to specify a location or an existing \
repository")
                sys.exit(1)


        app.environments.add(environment)

        try:
            app.save(username=args.username, password=args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        if args.raw:
            out.info(app.to_python())
        else:
            out.info("--> %s %s is created!" % (env.label.capitalize(), args.name))
            out.info("--> Details of the %s:\n" % env.label)
            output = ShowAction()
            args.type = "app"
            args.environment = args.environment
            output.show(args)

    ##
    # Create a repository
    ##
    @utils.arg('name',
            default=None,
            metavar="<name>",
            help="Name of the new resource")
    @utils.arg('location',
            default=None,
            metavar="<location>",
            help="URL of the repository")
    @utils.arg('--ssh-key',
            default=None,
            help="SSH key (password-less) for a SSH protected repository")
    def repository(self, args):
        """Create a new repository"""
        if args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()
        env.label = args.func.__name__

        Repository = utils._get_document(env.label.capitalize())
        repository = Repository({'name': args.name})
        repository.location = args.location

        if args.ssh_key:
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
            out.info("--> %s %s is created!" % (env.label.capitalize(), args.name))
            out.info("--> Details of the %s:\n" % env.label)
            output = ShowAction()
            args.type = "repository"
            args.environment = None
            output.show(args)

    ##
    # Create an environment
    ##
    @utils.arg('app',
            default=None,
            metavar='<app>',
            help="Name of the app")
    @utils.arg('environment',
            default=None,
            metavar='<environment>',
            help="Name of the new environment")
    @utils.arg('--cname',
            default=None,
            action="append",
            help="Comma separated list of cnames")
    @utils.arg('--root',
            default=".",
            help='Root directory of the application')
    @utils.arg('--backends',
            default=1,
            help="The number of backends to deploy on")
    @utils.arg('--flavor',
            default=None,
            choices=['django', 'wsgi'],
            required=True,
            help="The flavor of the app.")
    @utils.arg('--repo-branch',
            default="master",
            help="Branch of the repository to clone")
    @utils.arg('--repo-commit',
            default="HEAD",
            help="Commit of the repository to clone")
    @utils.arg('--requirements',
            default="requirements.txt",
            help="Requirements to install")
    @utils.arg('--inject-db',
            default=None,
            choices=['true', 'false'],
            help="Inject database settings into the settings file")
    @utils.arg('--django-settings-module',
            default="settings",
            help='Django settings module')
    @utils.arg('--wsgi-entrypoint',
            default="",
            help='Entrypoint of the application')
    def environment(self, args):
        """Create an environment for an existing app"""
        if args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        env.label = "app"
        env.resource = args.app

        app = args.app

        Environment = utils._get_document('PythonEnvironment')
        environment = Environment({'name': args.environment},
                context={'app': app})
        environment.requirements_file = args.requirements

        Backend = utils._get_document('Backend')
        backend = Backend({'region': "eu1", "count": args.backends})
        environment.backends.add(backend)

        if args.cname:
            Cname = utils._get_document('CnameRecord')
            for c in args.cname:
                cname = Cname({'record': c})
                environment.cname_records.add(cname)

        if args.flavor:
            environment.flavor = args.flavor
            flavor = getattr(environment, "%sflavor" % args.flavor)
            flavor.bound = True

            if args.inject_db:
                flavor.inject_db = args.inject_db.capitalize()

            for key, value in args.__dict__.iteritems():
                if key.startswith(args.flavor):
                    setattr(flavor, key, value)

        environment.requirements_file = args.requirements
        environment.repo_branch = args.repo_branch
        environment.repo_commit = args.repo_commit
        environment.project_root = args.root

        try:
            environment.save(username=args.username, password=args.password)
        except HttpBackendError as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        if args.raw:
            out.info(app.to_python())
        else:
            out.info("--> %s %s of app %s is created!" % (
                env.label.capitalize(),
                args.environment,
                args.app))
            out.info("--> Details of the %s:\n" % env.label)
            output = ShowAction()
            args.type = "environment"
            args.name = args.app
            args.environment = args.environment
            output.show(args)


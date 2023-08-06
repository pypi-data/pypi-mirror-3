"""
Thpppt - New things are shiny!
"""
import ConfigParser
import datetime
import sys
import traceback

import argparse
import envoy
import ffs
import jinja2

from _version import __version__

IGNORE = [
    ('tmpfiles', ['*~', '*#', '*.swp']),
    ('structural', ['build', 'dist']),
    ('translations', ['*.mo'])
    ]

PYIGNORE = [
    ('bytecode', ['*.py[co]']),
    ('packaging', ['*.egg', '*.egg-info', 'dist', 'eggs', 'parts', 'develop-eggs', 'MANIFEST']),
    ('installer', ['pip-log.txt']),
    ('testing', ['.coverage', '.tox']),
    ('documentation', ['doc/build'])
    ]

EMACSIGNORE = [
    ('bytecode', ['*.elc'])
    ]

ROOT = ffs.Path(__file__).parent
TEMPL = ROOT + 'templates'


class Error(Exception): pass
class TemplateNotFoundError(Error): pass

class IniParser(ConfigParser.SafeConfigParser):
    """
    Add a default option to ConfigParser.get
    """

    def get(self, section, option, default=None, vars=None):
        """
        Retrieve OPTION from SECTION, defaulting to DEFAULT

        Arguments:
        - `section`:str
        - `option`: str
        - `default`: object

        Return: object
        Exceptions: None
        """
        try:
            return ConfigParser.SafeConfigParser.get(self, section, option, vars=vars)
        except ConfigParser.NoSectionError:
            return default
        except ConfigParser.NoOptionError:
            return default

    def items(self, section, vars=None):
        """
        Return a list of (NAME, VALUE) tuples from SECTION or None

        Arguments:
        - `section`: str
        - `vars`: dict

        Return: list
        Exceptions: None
        """
        try:
            return ConfigParser.SafeConfigParser.items(self, section, vars=vars)
        except ConfigParser.NoSectionError:
            return []




dotfile = IniParser()
_dotpath = ffs.Path('~/.thpppt').abspath
if _dotpath:
    dotfile.readfp(_dotpath)

def render(path, template, variables = {}, searchpath = []):
    """
    Render TEMPLATE at PATH, interpolating VARIABLES.

    We pass dotfile implicitly.
    We look in templates/flavour, before templates for our template.
    If SEARCHPATH is defined, we look there frist.

    Arguments:
    - `path`: Path
    - `template`: str
    - `variables`: dict

    Return: None
    Exceptions: None
    """
    variables['dotfile'] = dotfile
    tplname = '{0}.jinja2'.format(template)
    tpl = None
    if searchpath:
        for p in searchpath:
           tpl = p + tplname
           if tpl:
               break
    if not tpl:
        tpl = TEMPL + [args.flavour, tplname]
    if not tpl:
        tpl = TEMPL + tplname
    if not tpl:
        raise TemplateNotFoundError('Could not find {0}'.format(tplname))
    template = jinja2.Template(tpl.contents)
    contents = template.render(**variables)
    path << contents
    return

def variable(name, default, ask=False, cache={}):
    """
    Get the variable NAME, falling back to DEFAULT if we can't find it.
    The heuristic to determine NAME is as follows:

    * If NAME is in our cache, use that.
    * If NAME is in our commandline arguments, use that.
    * If NAME is in ~/.thpppt [self.flavour], use that
    * If NAME is in ~/.thpppt [config], use that
    * If ASK is truthy and asking is not disabled in ~/.thpppt, get a value
      from raw_input(ASK)
    * Use default.

    Arguments:
    - `name`: str
    - `default`: str
    - `ask`: bool

    Return: str
    Exceptions: None
    """
    if name in cache:
        return cache[name]

    fromargs = getattr(args, name, None)
    if fromargs:
        cache[name] = fromargs
        return fromargs
    fromflavour = dotfile.get(args.flavour, name, None)
    if fromflavour:
        cache[name] = fromflavour
        return fromflavour
    fromconf = dotfile.get('config', name, None, vars={'name': args.name})
    if fromconf:
        cache[name] = fromconf
        return fromconf
    if ask:
        can_ask = dotfile.get('config', 'ask', 'true').lower().strip()
        if can_ask in ['t', 'true', 'y', 'yes']:
            prompt = '{0} [{1}]: '.format(ask, default)
            raw = raw_input(prompt)
            if raw:
                cache[name] = raw
                return raw
    cache[name] = default
    return default


class Repo(object):
    """
    Base Class for representing VCS repos.

    We expect this to be subclassed to be usable.

    We expect the class variable CMD to be set, representing the command
    one uses to invoke the VCS.

    We expect the class variable IGNORENAME to be set, representing the file
    to specify ignore patterns
    """
    cmd = 'cripes'
    ignorename = 'cripes'

    def __init__(self, root):
        self.root = root
        self.ignorefile = self.root + self.ignorename

    def init(self):
        """
        Initialize the Repo.
        """
        command = '{0} init {1}'.format(self.cmd, self.root)
        resp = envoy.run(command)
        return resp.status_code == 0

    def ignore(self, *args, **kw):
        """
        Add a line for each pattern in *ARGS to the repo's ignore file.

        If EXPLANATION is set, add this text as a comment.

        Arguments:
        - `explanation`: str
        - `*args`: str

        Return: None
        Exceptions: None
        """
        explanation = kw.get('explanation', None)
        if explanation:
            comment = '# {0}'.format(explanation)
        else:
            comment = '# Added by Thpppt({0}) {1}'.format(
                __version__, datetime.datetime.now().isoformat())

        self.ignorefile << "\n"
        self.ignorefile << comment + "\n"
        for pattern in args:
            self.ignorefile << "{0}\n".format(pattern)
        self.ignorefile << "\n"


class Git(Repo):
    """
    A representation of the Git Source Control Management System.
    """
    cmd = 'git'
    ignorename = '.gitignore'

    def init(self, bare=False):
        """
        Initialize the Git repo.

        If bare is True, pass the --bare argument

        Arguments:
        - `bare`: bool

        Return: None
        Exceptions: None
        """
        command = '{0} init {1} {2}'.format(self.cmd, '--bare' if bare else '', self.root)
        resp = envoy.run(command)
        return resp.status_code == 0

class HG(Repo):
    """
    A Mercurial repo.
    """
    cmd = 'hg'
    ignorename = '.hgignore'


def get_vcs(name):
    """
    Get the Repo class named NAME

    Arguments:
    - `name`: str

    Return: Repo
    Exceptions: None
    """
    vcsmap = {
        'git': Git,
        'hg': HG,
        'mercurial': HG
        }
    if name.lower() in vcsmap:
        return vcsmap[name.lower()]


class Project(object):
    """
    Base class for all Projects.

    Arguments:
    - `name`: str

    """
    def __init__(self, name, vcs=None, version='0.0.1'):
        """
        Setup instance state
        """
        self.name = name
        self.root = ffs.Path(name).abspath
        self.readme_file = None
        if vcs and not args.novcs:
            vcs = get_vcs(vcs)
            self.vcs = vcs(self.root)
        else:
            self.vcs = None
        self.version = version

    def init(self):
        """
        Take basic project initialization steps...

        It is expected that this method will be overridden by
        subclasses but still called, just as it is expected that
        certain of the interfaces called by this method will be
        overridden.

        * Create root directory
        * Initialize a VCS
        * If we have configured a build system stub, set that up
        * If we have configured a license, add that.
        * Create a Readme
        * Create a Documentation stub
        """
        if not self.root.is_dir and not self.root:
            self.root.mkdir()

        if self.vcs:
            self.vcs.init()
            for section, patterns in IGNORE:
                self.vcs.ignore(*patterns, explanation=section)

        self.build_system()
        self.license()
        self.document()
        return

    def render(self, path, template, searchpath=[], **kw):
        """
        Render TEMPLATE to PATH, passing **KW

        Implicitly add name, version, vcs, README to the template variables.
        If searchpath is non-null, look in these directories for templates as well.

        Arguments:
        - `path`: Path
        - `template`: str
        - `**kw`: str

        Return: None
        Exceptions: None
        """
        variables = {
            'name': self.name,
            'version': self.version,
            'readme': self.readme_file,
            'vcs': self.vcs.cmd if self.vcs else '',
            }
        variables.update(kw)
        render(path, template, variables, searchpath=searchpath)
        return

    def document(self):
        """
        Create our documentation stubs.

        This will as a minimum, create a README in ROOT and a doc directory
        """
        readme_ext = variable('readme', '')
        extension =  readme_ext and '.' + readme_ext or ''
        self.readme_file
        self.root.touch('README{0}'.format(extension))
        self.root.mkdir('doc')
        return

    def license(self):
        """
        Add a COPYING.txt to our project's root.

        Return: None
        Exceptions: None
        """
        license = variable('license', None)
        if license:
            self.render(self.root + 'COPYING.txt', license, searchpath=[TEMPL + 'licenses'])

    def build_system(self):
        """
        Create an entrypoint for our build system of choice.

        Return: None
        Exceptions: None
        """
        buildmap = {
            'rake': ('Rakefile', 'rakefile'),
            'make': ('Makefile', 'makefile')
            }
        buildsys = variable('build-system', None)
        if buildsys:
            filename, tplname = buildmap[buildsys]
            self.render(self.root + filename, tplname)


class PythonProject(Project):
    """
    Start a regular Python Project.
    """
    def init(self):
        """
        In addition to the Project init(),

        * Make NAME A Python Package with a _version.py set to VERSION
        * Add a setup.py whose name is NAME and version comes from _version.py
        * Add a MANIFEST.in
        * Add a blank requirements.txt
        * Add standard Python things to the VCS ignorefile.

        Return:
        Exceptions:
        """
        super(PythonProject, self).init()
        package = self.root + self.name
        package.mkdir()
        self.render(package + '_version.py', 'pyversion')
        self.render(package + '__init__.py', 'pyinit')

        setupdict = {}
        for var in ['author', 'email', 'url', 'description']:
            setupdict[var] = variable(var, None, ask=var.upper())
        self.render(self.root + 'setup.py', 'pysetup', **setupdict)
        self.render(self.root + 'MANIFEST.in', 'pymanifest')
        self.root.touch('requirements.txt')
        if self.vcs:
            for section, patterns in PYIGNORE:
                self.vcs.ignore(*patterns, explanation=section)
        return

    def sphinx(self):
        """
        Initialize Sphinx documentation for this project.


        Return: None
        Exceptions: None
        """
        try:
            from sphinx import quickstart
        except ImportError:
            print "Can't import Sphinx. Skipping"
            return

        sphinxopts = dict(dotfile.items('sphinx'))
        for f in sphinxopts:
            if sphinxopts[f] in ['False']:
                sphinxopts[f] = False
            if sphinxopts[f] in ['True']:
                sphinxopts[f] = True

        sphinxopts['path'] = self.root + 'doc'
        sphinxopts['project'] = args.name
        if variable('author', None, ask = 'Project Author'):
            sphinxopts['author'] = variable('author', None)
        sphinxopts['version'] = self.version
        sphinxopts['release'] = self.version

        quickstart.ask_user(sphinxopts)
        quickstart.generate(sphinxopts)
        return

    def document(self):
        """
        Do the standard documentation stuff, then:

        * Run sphinx-quickstart

        Return: None
        Exceptions: None
        """
        super(PythonProject, self).document()
        if not args.nosphinx:
            self.sphinx()
        return

class EmacsProject(Project):
    """
    Start an Emacs Lisp project.
    """

    def init(self):
        """
        Project.init() then...

        * Add the source file
        * Add a packege.el file
        * Add Emacs things to the VCS ignores
        """
        super(EmacsProject, self).init()
        self.root.touch('{0}.el'.format(self.name))
        pkgfile = self.root + '{0}-package.el'.format(self.name)
        self.render(pkgfile, 'pkg')
        if self.vcs:
            for section, patterns in EMACSIGNORE:
                self.vcs.ignore(*patterns, explanation=section)


def startproject(klass):
    """
    Start a KLASS project


    Arguments:
    - `klass`: Project

    Return: None
    Exceptions: None
    """
    kw = dict()

    kw['vcs'] = variable('vcs', None, ask='Version control system')
    version = variable('version', None)

    if version:
        kw['version'] = version

    proj = klass(args.name, **kw)
    proj.init()
    return

def main_python():
    """
    Start a Python project

    Return: int
    Exceptions: None
    """
    startproject(PythonProject)
    return 0

def main_emacs():
    """
    Start an Emacs Project

    Return: int
    Exceptions: None
    """
    startproject(EmacsProject)
    return 0

def main():
    """
    The commandline entrypoint to the program
    """
    globalargs = [
        [('name', ), dict(help='Name of the project')],
        [('-b', '--build-system'), dict(help='Build system to use', choices=['rake', 'make'])],
        [('-d', '--description'), dict(help='Short description of this project')],
        [('-l', '--license'), dict(help='License to use', choices = ['apache', 'gpl', 'lgpl'])],
        [('-v', '--version'), dict(help='Version to start the project at')],
        [('--directory', ), dict(help='Directory to start the project in')],
        [('--vcs', ), dict(help="Version Control System to use.", choices = ['git', 'hg'])],
        [('--novcs', ), dict(help="Do not enable a VCS system. This can only be set from the commandline\
 and overrides any other vcs arguments.", action = "store_true")],
        [('--author', ), dict(dict(help="Author of this project"))],
        [('--email', ), dict(help="Contact email for this project")],
        [('--url', ), dict(help="URL for this project")],
        ]

    description = "Thpppt: Let's build something shiny!"
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers(title='Commands')

    pyparser = subparsers.add_parser('python', help='Start a Python project',
                                     description = "Start a shiny Python project!")
    [pyparser.add_argument(*args, **kwargs)for args, kwargs in globalargs]
    pyparser.add_argument('--nosphinx', help='Do not initialize Sphinx documentation',
                          action = "store_true")
    pyparser.set_defaults(func=main_python, flavour='python')

    emacsparser = subparsers.add_parser('emacs', help='Start an Emacs Lisp project',
                                        description="Start a shiny Emacs Lisp project!")
    [emacsparser.add_argument(*args, **kwargs)for args, kwargs in globalargs]
    emacsparser.set_defaults(func=main_emacs, flavour='emacs')

    global args
    args = parser.parse_args()

    try:
        retval = args.func()
        return retval
    except Exception as err:
        traceback.print_exc()
        return - 1


if __name__ == '__main__':
    retval = main()
    sys.exit(retval)

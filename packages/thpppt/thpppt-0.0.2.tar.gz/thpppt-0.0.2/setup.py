import re
import os

from distutils.core import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'HISTORY.rst')).read()

VERSION_FILE = os.path.join(here, "thpppt/_version.py")
verstrline = open(VERSION_FILE, "rt").read()
VSRE = r'^__version__ = [\'"]([^\'"]*)[\'"]'
mo = re.search(VSRE,  verstrline, re.M)
if mo:
    VERSION = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in {0}".format(VERSION_FILE))

def get_template_dirs():
    tpldirs = ['templates/*.jinja2']
    killit = os.path.join(here, 'thpppt') + '/'
    for root, dirs, files in os.walk(os.path.join(here, 'thpppt/templates')):
        for subdir in dirs:
            tpldirs.append('{0}/*.jinja2'.format(os.path.join(root, subdir).replace(killit, '')))
    return tpldirs

print get_template_dirs()

setup(
    name = "thpppt",
    version = VERSION,
    author = "David Miller",
    author_email = "david@deadpansincerity.com",
    url = "www.deadpansincerity.com",
    description = "THPPPT!",
    long_description = README + "\n\n" + CHANGES,
    install_requires = [
#        'argparse',
#        'envoy'
        ],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2.6",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries"
        ],
    packages = ['thpppt'],
    include_package_data = True,
    package_data = {
        'thpppt': get_template_dirs(),
        },
    entry_points =  {
        'console_scripts': [
            'thpppt = thpppt:main'
            ]
        }
    )

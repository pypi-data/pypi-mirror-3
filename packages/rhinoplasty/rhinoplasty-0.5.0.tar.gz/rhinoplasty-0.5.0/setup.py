"""Packaging."""

import os
import re
from setuptools import find_packages
from setuptools import setup


## Helper Functions ##
def read(fname):
    """Import another file into the setup function.
    
    Taken from the example PyPI project. See
        http://packages.python.org/an_example_pypi_project/setuptools.html
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_package_version():
    version_module = os.path.join(os.path.dirname(__file__), "rhinoplasty", "_version.py")
    for line in open(version_module):
        match = re.search('''__version__ *= *['"]([0-9.]+)['"]''', line)
        if match is not None:
            return match.group(1)
    raise Exception("Package version could not be found")


## Run Setup ##
setup(
    name = "rhinoplasty",
    version = get_package_version(),
    author = "Gary Donovan",
    author_email = "garyd@crucialfruit.com.au",
    url = "N/A", #FIXME get a URL
    license = "LGPL",
    keywords = "Nose test unittest",
    description = ("Experimental extensions and helper functions for the Nose test runner."),
    long_description = read('README.txt'),
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Topic :: Software Development :: Testing",
    ],
    packages = find_packages("."),
    entry_points = {
        'nose.plugins.0.10': [
            "rich-errors = rhinoplasty.rich_errors.plugin:RichErrorReportingPlugin",
        ],
    },
)

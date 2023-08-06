# coding: utf-8
from __future__ import absolute_import, print_function
from distutils.core import setup, Command
import sys
requires_list = [
        "PyYAML (>=3.09)"
    ]
try:
    import unittest2 as unittest
except ImportError:
    import unittest
else:
    if sys.version_info <= (2 , 6):
        requires_list.append("unittest2")
import os.path
import yamlish

class RunTests(Command):
    """New setup.py command to run all tests for the package.
    """
    description = "run all tests for the package"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        tests = unittest.TestLoader().discover('.')
        runner = unittest.TextTestRunner()
        runner.run(tests)

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as inf:
        return "\n" + inf.read().replace("\r\n", "\n")

setup(
    name='yamlish',
    version=str(yamlish.__version__),
    description='Python implementation of YAMLish',
    author='Matěj Cepl',
    author_email='mcepl@redhat.com',
    url='https://gitorious.org/yamlish',
    py_modules=['yamlish'],
    long_description=read("README.txt"),
    keywords=['TAP', 'YAML', 'yamlish'],
    cmdclass={'test': RunTests},
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
        ],
    requires=requires_list
)

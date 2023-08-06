# coding: utf-8
from __future__ import absolute_import, print_function
from distutils.core import setup, Command
import sys
requires_list = ["yamlish"]
try:
    import unittest2 as unittest
except ImportError:
    import unittest
else:
    if sys.version_info <= (2 , 6):
        requires_list.append("unittest2")
import os.path
import unittest_TAP
import tap
from test import test_tap, example_unittest

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
        tests = unittest.TestLoader().loadTestsFromModule(test_tap)
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(tests)


class RunExamples(Command):
    """New setup.py command to run example use of the unittest_TAP module.
    """
    description = "run example use of the unittest_TAP module"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        tests = unittest_TAP.TestLoader().loadTestsFromModule(example_unittest)
        runner = unittest_TAP.TAPTestRunner(verbosity=2)
        runner.run(tests)


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as inf:
        return "\n" + inf.read().replace("\r\n", "\n")

setup(
    name='bayeux',
    version=str(tap.__version__),
    description='Generator of the TAP protocol',
    author=u'Matěj Cepl',
    author_email='mcepl@redhat.com',
    url='https://gitorious.org/bayeux/bayeux',
    py_modules=['tap', 'unittest_TAP'],
    scripts=['generate_TAP'],
    long_description=read("README.txt"),
    keywords=['TAP', 'unittest'],
    cmdclass={
              'test': RunTests,
              'examples': RunExamples},
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
    requires=requires_list,
)

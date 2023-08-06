#!/usr/bin/env python

from distutils.core import setup, Command
from os.path import join, dirname, abspath
import re

import uprefix

class TestCommand(Command):
    user_options = []

    def run(self):
        import sys
        import unittest

        import test_uprefix
        loader = unittest.TestLoader()
        runner = unittest.TextTestRunner()
        runner.run(loader.loadTestsFromModule(test_uprefix))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

def description():
    f = open(join(dirname(__file__), 'README'))
    read_me = f.read()
    f.close()
    regexp = r'^uprefix\s*[\d.]*\s*\n=======+\s*\n(.*)Requirements '
    requires, = re.findall(regexp, read_me, re.DOTALL)
    regexp = r'Availability & Documentation\s*\n-----+\s*\n(.*)'
    avail, = re.findall(regexp, read_me, re.DOTALL)
    return requires + avail

setup(
    name='uprefix',
    description=('An import hook for Python 3 that removes u prefixes '
                 'from Python source code before compiling it.'),
    long_description=description(),
    version=uprefix.__version__,
    author='Vinay Sajip',
    author_email='vinay_sajip@yahoo.co.uk',
    maintainer='Vinay Sajip',
    maintainer_email='vinay_sajip@yahoo.co.uk',
    url='https://bitbucket.org/vinay.sajip/uprefix/',
    packages=['uprefix'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: Implementation',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    cmdclass={ 'test': TestCommand },
)

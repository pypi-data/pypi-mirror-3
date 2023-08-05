#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from distutils.core import setup
from setuptools.command import install

version_tuple = __import__('swissknife').VERSION
version = '.'.join([str(v) for v in version_tuple])

class DoInstall(install.install):
    def run(self):
        raise Exception('Python is already installed on your system (%s)' % (sys.executable))

setup(
    name = 'swissknife',
    version = version,
    description = 'Swissknife',
    author = 'Bernhard Janetzki',
    author_email = 'boerni@gmail.com',
    url = 'https://bitbucket.org/boerni/swissknife',
    packages = ['swissknife'],
    cmdclass = {'install': DoInstall},
)
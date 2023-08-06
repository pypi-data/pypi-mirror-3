#!/usr/bin/env python

from distutils.core import setup

# py3 compat
try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    # 2.x
    from distutils.command.build_py import build_py

setup(name='piston-mini-client',
    version='0.7',
    description='A package to consume Django-Piston web services',
    url='https://launchpad.net/piston-mini-client',
    author='Anthony Lenton',
    author_email='anthony.lenton@canonical.com',
    packages=['piston_mini_client'],
    license='LGPLv3',
    install_requires=[
        'oauth',
        'httplib2',
    ],
    cmdclass = {'build_py':build_py}
)

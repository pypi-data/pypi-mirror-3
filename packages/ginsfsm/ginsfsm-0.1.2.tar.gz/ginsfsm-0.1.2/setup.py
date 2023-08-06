# -*- encoding: utf-8 -*-

import os
import sys

from setuptools import setup, find_packages

if sys.version_info[:2] < (2, 6):
    raise RuntimeError('Requires Python 2.6 or better')

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

version = '0.1.2'

setup(name='ginsfsm',
    version=version,
    description='GinsFSM, a library to develop systems based in '
                'finite-state machines',
    long_description=README + "\n\n" +  CHANGES,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Communications",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: ISC License (ISCL)",
        ],
    keywords='framework communication finite state machine fsm '
             'socket poll epoll kqueue select server client workflow',
    author='Ginés Martínez Sánchez',
    author_email='ginsmar@artgins.com',
    url='http://ginsfsm.org',
    license='ISC License (ISCL)',
    packages=find_packages(exclude=[]),
    include_package_data=True,
    zip_safe=False,
    install_requires = [],
    tests_require = [],
    test_suite="ginsfsm.tests",
    entry_points="""
    """,
    )

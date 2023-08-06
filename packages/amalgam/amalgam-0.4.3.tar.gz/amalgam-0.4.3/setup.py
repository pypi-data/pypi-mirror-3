#!/usr/bin/env python

import os.path as op
act = op.join(op.dirname(__file__), 'venv', 'bin', 'activate_this.py')
if op.exists(act):
    execfile(act, {'__file__': act})

import os.path
from setuptools import setup, find_packages

import amalgam


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setupconf = dict(
    name = 'amalgam',
    version = amalgam.__version__,
    license = 'BSD',
    url = 'http://hg.piranha.org.ua/amalgam/',
    author = 'Alexander Solovyov',
    author_email = 'alexander@solovyov.net',
    description = ('Minimal wrapper for database access'),
    long_description = read('README'),

    packages = find_packages(),

    install_requires=['ordereddict'], #'SQLAlchemy>=0.6'],
    test_suite='tests',

    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database :: Front-Ends',
        ],
    )

if __name__ == '__main__':
    setup(**setupconf)

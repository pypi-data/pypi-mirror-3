#!/usr/bin/env python2
# coding=utf-8

# Last modified: <2012-07-18 19:08:40 Wednesday by richard>

# @version 0.1
# @author : Richard Wong
# Email: chao787@gmail.com

# public lisence: BSD
import os
from setuptools import find_packages, setup

from _version import version

readme = open(os.path.join(os.path.dirname(__file__), 'README')).read()

setup(
    name = 'python_org',
    description = 'Fast most-functional organizer for org-mode.',
    long_description = readme,


    # technical info
    version = version,
    packages = find_packages(),
    requires = [
        'python (>= 2.6)',
    ],
    provides = ['python_org'],
    # extras_require = {
    # }

    # copyright
    author   = 'Richard Wong',
    author_email = 'chao787@gmail.com',
    license="Two-clause BSD license",

    # # more info
    # url          = 'http://bitbucket.org/neithere/orgtool/',
    # download_url = 'http://bitbucket.org/neithere/orgtool/src/',


    # misc settings.
    zip_safe=True,
    # test_suite="nose.collector",


    # categorization
    keywords = ('query database api model models orm key/value '
                'orgtoolment-oriented org-mode non-relational emacs'),
    classifiers  = [
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Database',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Database :: Front-Ends',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],


)
# setup.py ended here

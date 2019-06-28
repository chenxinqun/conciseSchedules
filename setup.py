#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@File  : setup.py
@Author: XinQun
@Date  : 2019/1/18 16:26
@Company: 宏数科技
'''
import sys
import pathlib
from setuptools import (
    setup,
    find_packages
)

if sys.version_info < (3, 5, 0):
    raise RuntimeError("conciseSchedules 1.x requires Python 3.5.0+")

here = pathlib.Path(__file__).parent


def read(f):
    return (here / f).read_text('utf-8').strip()


about = {}

version = (here / 'conciseSchedules' / '__init__.py').read_text('utf-8')
exec(version.split('###===###')[0], about)

install_requires = [
    'pytz',
    'tzlocal',
]

args = dict(
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Software Development :: Libraries :: Python Modules',

    ],
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    maintainer=about['__maintainer__'],
    maintainer_email=about['__maintainer_email__'],
    license=about['__license__'],
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    python_requires='>=3.5.0',
    install_requires=install_requires,
    include_package_data=True,
)

setup(**args)

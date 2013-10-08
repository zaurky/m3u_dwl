#!/usr/bin/env python
from os import path

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

README = path.abspath(path.join(path.dirname(__file__), 'README.md'))
desc = 'A Python util to easily download streaming videos in m3u format'

setup(
    name='m3u_dwl',
    version='0.0.1',
    author='Zaurky',
    author_email='zaurky@zeb.re',
    description=desc,
    long_description=open(README).read(),
    license='GPLV2',
    url='http://github.com/zaurky/m3u_dwl',
    packages=['m3u_dwl'],
    scripts=['bin/m3u_dwl'],
    install_requires=[
        'BeautifulSoup',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)

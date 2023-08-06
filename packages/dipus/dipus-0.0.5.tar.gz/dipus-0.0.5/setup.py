import os
import sys

from setuptools import setup, find_packages


requirements = [
    "bottle",
    "sphinx",
    "whoosh",
    "docutils",
    "simplejson",
    ]

classifiers = [
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python :: 2.7",
    "Topic :: Database :: Database Engines/Servers",
    "Topic :: Software Development :: Documentation",
    "Topic :: Documentation"
    ]

setup(
    name='dipus',
    version="0.0.5",
    description='Dipus is a simple full-text search server using Whoosh for Sphinx',
    long_description=open("README.rst").read(),
    classifiers=classifiers,
    keywords=['sphinx', 'whoosh', 'text search'],
    author='WAKAYAMA shirou',
    author_email='shirou.faw at gmail.com',
    url='http://bitbucket.org/r_rudi/dipus',
    license='BSD License',
    install_requires=requirements,
    package_dir={'': 'src'},
    packages = [
    'dipus',
    ],
    package_data={'': ['src/dipus/_static', 'src/dipus/_templates']},
    include_package_data=True
    )


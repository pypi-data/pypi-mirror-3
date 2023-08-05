#!/usr/bin/env python
import os
import sys

from setuptools import setup, find_packages

sys.path.insert(0, './src')
from consent import __version__

basePath = os.path.abspath(os.path.dirname(sys.argv[0]))
scripts = [ 
    os.path.join('bin', 'consent-admin'),
    os.path.join('bin', 'consent-makeconfig'),
    os.path.join('bin', 'consent-test'),
]

setup(
    name='consent',
    version=__version__,

    package_dir={'': 'src'},
    packages=find_packages('src'),
    scripts=scripts,
    # just use auto-include and specify special items in MANIFEST.in
    include_package_data = True,
    # ensure Consent is installed unzipped
    # this avoids potential problems when apache/modpython imports consent but
    # does not have right permissions to create an egg-cache directory
    # see:
    # http://mail.python.org/pipermail/python-list/2006-September/402300.html
    # http://docs.turbogears.org/1.0/mod_python#setting-the-egg-cache-directory
    zip_safe = False,

    install_requires = [
        'domainmodel==0.15',
        'Routes>=1.7.2,<=1.10.3',
    ],
    author='Appropriate Software Foundation',
    author_email='john.bywater@appropriatesoftware.net',
    license='AGPL',
    url='http://pypi.python.org/pypi/consent',
    description='Software for general assemblies',
    long_description = open('README').read(),
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

#!/usr/bin/env python
#
# Copyright (c) 2008-2012 Thomas Lotze
# See also LICENSE.txt

# This should be only one line. If it must be multi-line, indent the second
# line onwards to keep the PKG-INFO file format intact.
"""A paste.script template for a namespaced Python package and a Sphinx theme.
"""

from setuptools import setup, find_packages
import glob
import os.path


def project_path(*names):
    return os.path.join(os.path.dirname(__file__), *names)


setup(
    name='tl.pkg',
    version='0.1',

    install_requires=[
        'PasteScript',
        'distribute',
        ],

    extras_require={
        'doc': [
            'Sphinx>=1.0',
            'pkginfo',
            'sphinxcontrib-cheeseshop',
            'sphinxcontrib-issuetracker',
            ],
        'test': [
            'gocept.testing',
            'unittest2',
            ],
        },

    entry_points="""
        [console_scripts]
        doc=tl.pkg.doc:main

        [paste.paster_create_template]
        tl-pkg = tl.pkg.template:TLPkg
    """,

    author='Thomas Lotze',
    author_email='thomas@thomas-lotze.de',
    license='ZPL 2.1',
    url='https://bitbucket.org/tlotze/tl.pkg/',

    keywords=('paste.script paster create template python package '
              'sphinx docs theme development buildout'),
    classifiers="""\
Environment :: Plugins
Framework :: Paste
Intended Audience :: Developers
License :: OSI Approved :: Zope Public License
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 2 :: Only
"""[:-1].split('\n'),
    description=__doc__.strip(),
    long_description='\n\n'.join(open(project_path(name)).read() for name in (
            'README.txt',
            'ABOUT.txt',
            )),

    namespace_packages=['tl'],
    packages=find_packages(),
    include_package_data=True,
    data_files=[('', glob.glob(project_path('*.txt')))],
    zip_safe=False,
    )

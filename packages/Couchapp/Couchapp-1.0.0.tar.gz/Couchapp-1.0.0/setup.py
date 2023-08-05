# -*- coding: utf-8 -*-
#
# This file is part of couchapp released under the Apache 2 license. 
# See the NOTICE for more information.

from setuptools import setup, find_packages
from distutils.command.install_data import install_data
import glob
from imp import load_source
import os
import sys

if not hasattr(sys, 'version_info') or sys.version_info < (2, 6, 0, 'final'):
    raise SystemExit("Couchapp requires Python 2.6 or later.")


executables = []
setup_requires = []
extra = {}

couchapp = load_source("couchapp", os.path.join("couchapp",
        "__init__.py"))


def get_data_files():
    data_files = []
    data_files.append(('couchapp', 
                       ["LICENSE", "MANIFEST.in", "NOTICE", "README.rst",
                        "THANKS",]))
    return data_files


def ordinarypath(p):
    return p and p[0] != '.' and p[-1] != '~'

def get_packages_data():
    packagedata = {'couchapp': []}

    for root in ('templates',):
        for curdir, dirs, files in os.walk(os.path.join("couchapp", root)):
            curdir = curdir.split(os.sep, 1)[1]
            dirs[:] = filter(ordinarypath, dirs)
            for f in filter(ordinarypath, files):
                f = os.path.normpath(os.path.join(curdir, f))
                packagedata['couchapp'].append(f)
    return packagedata 


MODULES = [
        'couchapp',
        'couchapp.autopush',
        'couchapp.autopush.brownie',
        'couchapp.autopush.brownie.datastructures',
        'couchapp.autopush.pathtools',
        'couchapp.autopush.watchdog',
        'couchapp.autopush.watchdog.observers',
        'couchapp.autopush.watchdog.tricks',
        'couchapp.autopush.watchdog.utils',
        'couchapp.hooks',
        'couchapp.hooks.compress',
        'couchapp.restkit',
        'couchapp.restkit.manager',
        'couchapp.restkit.contrib',
        'couchapp.simplejson',
        'couchapp.vendors',
        'couchapp.vendors.backends',
    ]

CLASSIFIERS = [
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Database',
        'Topic :: Utilities',
    ]

def get_scripts():
    scripts = [os.path.join("resources", "scripts", "couchapp")]
    if os.name == "nt":
        scripts.append(os.path.join("resources", "scripts",
            "couchapp.bat"))
    return scripts

DATA_FILES = get_data_files()


def get_py2exe_datafiles():
    datapath = os.path.join('couchapp', 'templates')
    head, tail = os.path.split(datapath)
    d = dict(get_data_files())
    for root, dirs, files in os.walk(datapath):
        files = [os.path.join(root, filename) for filename in files]
        root = root.replace(tail, datapath)
        root = root[root.index(datapath):]
        d[root] = files
    return d.items()



if os.name == "nt" or sys.platform == "win32":
    # py2exe needs to be installed to work
    try:
        import py2exe

        # Help py2exe to find win32com.shell
        try:
            import modulefinder
            import win32com
            for p in win32com.__path__[1:]: # Take the path to win32comext
                modulefinder.AddPackagePath("win32com", p)
            pn = "win32com.shell"
            __import__(pn)
            m = sys.modules[pn]
            for p in m.__path__[1:]:
                modulefinder.AddPackagePath(pn, p)
        except ImportError:
            raise SystemExit('You need pywin32 installed ' +
                    'http://sourceforge.net/projects/pywin32')

        # If run without args, build executables, in quiet mode.
        if len(sys.argv) == 1:
            sys.argv.append("py2exe")
            sys.argv.append("-q")

        extra['console'] = [{
             'script': os.path.join("resources", "scripts", "couchapp"),
             'copyright':'Copyright (C) 2008-2011 Benoît Chesneau and others',
             'product_version': couchapp.__version__ 
        }]


    except ImportError:
        raise SystemExit('You need py2exe installed to run Couchapp.')

    DATA_FILES = get_py2exe_datafiles()

class install_package_data(install_data):
    def finalize_options(self):
        self.set_undefined_options('install',
                                   ('install_lib', 'install_dir'))
        install_data.finalize_options(self)


def main():
    # read long description
    with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
        long_description = f.read()

    INSTALL_REQUIRES=[
            'restkit',
            'watchdog']

    try:
        import json
    except ImportError:
        INSTALL_REQUIRES.append('simplejson')

    options = dict(
            name = 'Couchapp',
            version = couchapp.__version__,
            url = 'http://github.com/couchapp/couchapp/tree/master',
            license =  'Apache License 2',
            author = 'Benoit Chesneau',
            author_email = 'benoitc@e-engura.org',
            description = 'Standalone CouchDB Application Development Made Simple.',
            long_description = long_description,
            keywords = 'couchdb couchapp',
            platforms = ['any'],
            classifiers = CLASSIFIERS,
            packages = find_packages(),
            data_files = DATA_FILES,
            include_package_data=True,
            zip_safe=False, 
            install_requires = INSTALL_REQUIRES,
            scripts=get_scripts(),
            options = dict(py2exe={
                                'dll_excludes': [
                                    "kernelbase.dll",
                                    "powrprof.dll" 
                                ],
                                'packages': [
                                    "http_parser",
                                    "restkit",
                                    "restkit.manager",
                                    "restkit.contrib",
                                    "pathtools.path",
                                    "brownie",
                                    "brownie.datastructures",
                                    "watchdog",
                                    "watchdog.observers",
                                    "watchdog.tricks",
                                    "watchdog.utils",
                                    "win32pdh",
                                    "win32pdhutil",
                                    "win32api",
                                    "win32con",
                                    "subprocess"
                                ]
                           },

                           bdist_mpkg=dict(zipdist=True,
                                           license='LICENSE',
                                           readme='resources/macosx/Readme.html',
                                           welcome='resources/macosx/Welcome.html')
            )
    )
    options.update(extra)
    setup(**options)

if __name__ == "__main__":
    main()




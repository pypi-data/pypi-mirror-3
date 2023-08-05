#!/usr/bin/env python
"""Installs mockproc package (using setuptools)
"""
import os
from setuptools import setup

version = [
    (line.split('=')[1]).strip().strip('"').strip("'")
    for line in open(os.path.join( 'mockproc','__init__.py'))
    if line.startswith( '__version__' )
][0]

if __name__ == "__main__":
    extraArguments = {
        'classifiers': [
            """License :: OSI Approved :: BSD License""",
            """Programming Language :: Python""",
            """Topic :: Software Development :: Libraries :: Python Modules""",
            """Intended Audience :: Developers""",
        ],
        'keywords': 'mock,process,subprocess',
        'platforms': ['Any'],
    }
    ### Now the actual set up call
    setup (
        name = "MockProc",
        version = version,
        url = "https://launchpad.net/mockproc",
        download_url = "http://pypi.python.org/pypi/MockProc/",
        description = "Simple stubs/mocks for processes (mostly for use with Nose)",
        author = "Mike C. Fletcher",
        author_email = "mcfletch@vrplumber.com",
        install_requires = [
        ],
        license = "BSD",
        package_dir = {
            'mockproc':'mockproc',
        },
        packages = [
            'mockproc',
        ],
        options = {
            'sdist':{
                'force_manifest':1,
                'formats':['gztar','zip'],},
        },
        zip_safe=False,
        **extraArguments
    )


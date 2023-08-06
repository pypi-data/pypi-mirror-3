#!/bin/env python

from distutils.core import setup
from src.multicast import VERSION

setup ( name="py-multicast",
        description='Python Multicast Toolkit for Linux',
        version=VERSION,
        url='http://coobs.eu.org/py-multicast/',
        author='Jakub Wroniecki',
        author_email='wroniasty@gmail.com',
        packages = ["multicast" ],
        package_dir = { '' : 'src'},
        scripts = ['bin/udp-redirect.py'],
        license = "BSD",
        classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Networking',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Libraries :: Python Modules',                                    
        ],
        download_url = 'https://sourceforge.net/projects/py-multicast/files/',
        long_description = """
This is a simple python IP multicast library. It was developed and tested on Linux only, but should work on other POSIX OS'es.

`Documentation, examples <http://coobs.eu.org/py-multicast/>`_.

"""
        )

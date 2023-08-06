#!/usr/bin/env python3

from distutils.core import setup
import gravnoise as g

setup(
    name=g.__program_name__,
    version=g.__version__,
    author=g.__author_name__,
    author_email=g.__author_email__,
    package_dir={'': '.'},
    py_modules=[g.__program_name__],
    scripts=[g.__program_name__],
    url=g.__home_page__,
    license=g.__license_short__,
    description=g.__program_description__,
    long_description=open('README.txt').read(),
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Intended Audience :: End Users/Desktop',
                 'Environment :: Console',
                 'Topic :: Games/Entertainment',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Topic :: Software Development :: Libraries :: pygame',
                 'License :: DFSG approved',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.1'
                 ]
)

#!/usr/bin/env python3

from distutils.core import setup, Extension

_c_module = Extension('yelljfish._core', sources=[
        'yelljfish/core.c',
        'yelljfish/wrapper.c',
        ],
    include_dirs=[],
    library_dirs=[],
    libraries=['png'])

setup(
    name='yelljfish',
    version='0.1.0',
    author='Niels Serup',
    author_email='ns@metanohi.name',
    packages=['yelljfish'],
    scripts=['scripts/yelljfish'],
    url='http://metanohi.name/projects/yelljfish/',
    license='AGPLv3+',
    description='A pixel-based, potentially pseudo-random image generator',
    long_description=open('README.txt').read(),
    ext_modules = [_c_module],
    classifiers=['Development Status :: 3 - Alpha',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Education',
                 'Environment :: Console',
                 'Topic :: Multimedia :: Graphics',
                 'Topic :: Utilities',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Topic :: Other/Nonlisted Topic',
                 'License :: DFSG approved',
                 'License :: OSI Approved :: GNU Affero General Public License v3',
                 'Operating System :: OS Independent',
                 'Programming Language :: C',
                 'Programming Language :: Python :: 3.1'
                 ])

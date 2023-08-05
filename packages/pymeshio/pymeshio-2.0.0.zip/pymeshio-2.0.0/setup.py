#!/usr/bin/env python

from setuptools import setup
import sys
import os
import shutil

name='pymeshio'
version='2.0.0'
short_description='pure python 3d model io library'
long_description='''\
`pymeshio` is a package for 3d model io.
create for blender import/expoert plugin backend.

Requirements
------------
* Python 3

Features
--------
* read/write Metasequioa mqo format
* read/write MikuMikuDance pmd format
* read-only  MikuMikuDance pmx format
* read/write MikuMikuDance vmd format
* read/write MikuMikuDance vpd format


Setup
-----
::

   $ easy_install pymeshio
   or
   $ unzip pymeshio-x.x.x.zip
   $ cd pymeshio-x.x.x
   $ python setup.py install

History
-------
2.0.0 (2011-9-30)
~~~~~~~~~~~~~~~~~~
* add pmx loader

    >>> import pymeshio.pmx.loader
    >>> m=pymeshio.pmx.loader.load('resources/初音ミクVer2.pmx')
    >>> print(m)
    <pymeshio.pmx.Model object at 0x0281DD50>
    >>> print(m.name)
    初音ミク
    >>> print(m.english_name)
    Miku Hatsune

1.9.2 (2011-9-29)
~~~~~~~~~~~~~~~~~~
* add tkinter viewer sample

1.9.1 (2011-9-23)
~~~~~~~~~~~~~~~~~~
* register pypi
'''

classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: zlib/libpng License',
        'Topic :: Multimedia :: Graphics :: 3D Modeling',
        ]

# copy pymeshio dir for blender25 plugin
PYMESHIO_DIR_IN_BLENDER='blender25-meshio/pymeshio'
if os.path.exists(PYMESHIO_DIR_IN_BLENDER):
    shutil.rmtree(PYMESHIO_DIR_IN_BLENDER)    
print("copy pymeshio to blender-25")
shutil.copytree('pymeshio', PYMESHIO_DIR_IN_BLENDER)

setup(
        name=name,
        version=version,
        description=short_description,
        long_description=long_description,
        classifiers=classifiers,
        keywords=['mqo', 'pmd', 'pmx', 'vmd', 'vpd', 'mmd', 'blender'],
        author='ousttrue',
        author_email='ousttrue@gmail.com',
        url='http://meshio.sourceforge.jp/',
        license='zlib',
        #package_dir={
        #    'pymeshio': 'blender25-meshio/pymeshio'
        #    },
        packages=['pymeshio'],
        test_suite='nose.collector',
        tests_require=['Nose'],
        zip_safe = (sys.version>="2.5"),   # <2.5 needs unzipped for -m to work
        )


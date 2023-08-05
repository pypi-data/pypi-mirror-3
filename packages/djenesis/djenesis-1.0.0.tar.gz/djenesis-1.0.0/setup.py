#!/usr/bin/env python

from distutils.core import setup
import os
import djenesis


def walk_data_files(output_path, scan_dir):
    """Use os.walk() to build a data_files definition for setup()"""
    data_files = []
    for dirname, dirs, files in os.walk(scan_dir):
        files = filter(lambda f: not any([f.startswith('.'), f.endswith('.pyc')]), files)
        if len(files) > 0:
            output_dirname = os.path.join(output_path,dirname)
            files = [os.path.join(dirname, f) for f in files]
            data_files.append( (output_dirname, files) )
    return data_files

version = '.'.join(map(str, djenesis.VERSION))
description = 'Djenesis begets Django projects' 
try:
    long_description = open('README.rst').read()
except Exception as e:
    long_description = description

setup(
    # meta data
    name='djenesis',
    version=version,
    description=description,
    long_description=long_description,
    url='http://github.com/concentricsky/djenesis',
    author='Concentric Sky',
    author_email='code@concentricsky.com',
    classifiers=[
        'Environment :: Console',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Framework :: Django',
    ],

    # install data
    scripts=['scripts/djenesis'],
    packages=['djenesis'],
    data_files=walk_data_files('share/djenesis', 'templates'),
)

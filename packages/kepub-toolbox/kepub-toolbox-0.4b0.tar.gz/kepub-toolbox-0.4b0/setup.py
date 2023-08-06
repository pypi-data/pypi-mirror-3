#!/usr/bin/env python

from distutils.core import setup
import os

from kepub import get_version
 
# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('kepub'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[6:] # Strip "kepub/" or "kepub\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))

setup(
    name='kepub-toolbox',
    version=get_version().replace(' ', '-'),
    author='Pietro Spagnulo <pspagnulo@gmail.com>, Stefano Quaranta <steppo40@gmail.com>',
    author_email='pspagnulo@gmail.com, steppo40@gmail.com',
    description='Utilities for ebook format conversion',
    long_description=open('README.txt').read(),
    url='http://pypi.python.org/pypi/kepub-toolbox/',
    package_dir={'kepub': 'kepub'},
    packages=packages,
    package_data={'kepub': data_files},
    scripts=['bin/odt2docbook.py'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Java',
        'Topic :: Text Processing'
        ],
    license='LICENSE.txt',
    requires=['python (>= 2.6)']  
)

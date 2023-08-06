#!/usr/bin/env python
# Copyright (C) 2006, Martijn Pieters <mj@zopatista.com>
# This program is open source.  For license terms, see the LICENSE.txt file.

from distutils.core import setup
from distutils.command.build_py import build_py
import os

base = os.path.split(__file__)[0] or os.getcwd()
VERSION = file(os.path.join(base, "version.txt")).readline().strip()

# Build package and data_files structures
data_globs = ['*.txt', '*.pt', '*.zcml']
packages = ['z3wingdbg']
package_data=dict(
    z3wingdbg=data_globs + ['locales/*.pot', 'locales/*/*/*.po', 
                            'locales/*/*/*.mo'])
for path, dirs, files in os.walk(base):
    for dir in list(dirs):
        if os.path.exists(os.path.join(path, dir, '__init__.py')):
            package_base = filter(None, path[len(base):].split(os.path.sep))
            package = '.'.join(['z3wingdbg'] + package_base + [dir])
            packages.append(package)
            package_data[package] = data_globs[:]
        else:
            dirs.remove(dir)
        
# Distutils adjustments (*sigh*)
class fixed_build_py(build_py):
    """Bug-fixed version of get_data_files"""
    def get_data_files (self):
        """Generate list of '(package,src_dir,build_dir,filenames)' tuples"""
        data = []
        if not self.packages:
            return data
        for package in self.packages:
            # Locate package source directory
            src_dir = self.get_package_dir(package)

            # Compute package build directory
            build_dir = os.path.join(*([self.build_lib] + package.split('.')))

            # Length of path to strip from found files (if src_dir != '')
            plen = len(src_dir) and len(src_dir)+1

            # Strip directory from globbed filenames
            filenames = [
                file[plen:] for file in self.find_data_files(package, src_dir)
                ]
            data.append((package, src_dir, build_dir, filenames))
        return data
    
setup(
    name='z3wingdbg',
    version=VERSION,
    description='Wing IDE debugger integration for Zope3',
    long_description='''\
Zope3 package providing debug integration with the `Wing IDE`_, allowing you to
run Zope3 applications under the control of the Wing debugger.

.. _Wing IDE: http://wingide.com

''',
    license='ZPL 2.1',
    platforms='POSIX, Windows',
    author='Martijn Pieters',
    author_email='mj@zopatista.com',
    url='http://www.zopatista.com/projects/z3wingdbg',
    download_url='http://www.zopatista.com/projects/z3wingdbg/'
                 'releases/%s/z3wingdbg-%s.tar.gz' % (VERSION, VERSION),
    keywords='debugger,Zope3,Wing IDE,HTTP',
    packages=packages,
    package_data=package_data,
    package_dir=dict(z3wingdbg=''),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Debuggers',
    ],
    cmdclass = dict(build_py=fixed_build_py)
)

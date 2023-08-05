#!/usr/bin/python

import os
import sys
from distutils.command.install import INSTALL_SCHEMES
from distutils.command.install_data import install_data
from distutils.core import setup

#REVIEW: Okay this is super ugly, but it'll at least allow for this package to be pippable.
from subprocess import call
call(["cmake", os.path.join(os.path.dirname(__file__),  "pylinkgrammar")])
call(["make"])

#Further horribleness.  Surely there is a way to make make put stuff where we want it, or to make
#cmake tell its makefile to do that, but for now, this works.
import shutil
for f in ["clinkgrammar.py", "_clinkgrammar.so"]:
    shutil.move(os.path.join(os.path.dirname(__file__), f), os.path.join(os.path.dirname(__file__), "pylinkgrammar", f))

cmdclasses = {'install_data': install_data}

# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

# We need to walk down the directory we are in, and add any packages we find to a list of
# packages. This trick was stolen from Django's setup.py.
def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages = []
data_files = []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
code_dir = 'pylinkgrammar'

for dirpath, dirnames, filenames in os.walk(code_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    if filenames:
        non_python_filenames = []
        for filename in filenames:
            if not (filename.endswith('.py') or filename.endswith('.pyc')):
                non_python_filenames.append(filename)
        data_files.append([dirpath,
             [os.path.join(dirpath, f) for f in non_python_filenames]])

setup(name='pylinkgrammar', version='0.1.7',
    description='Python bindings for Link Grammar system',
    author='MetaMetrics, Inc.',
    packages=packages,
    data_files=data_files,
    cmdclass = cmdclasses)

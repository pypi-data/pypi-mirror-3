#!/usr/bin/env python
#
#   PyCOM - Distributed Component Model for Python
#   Copyright (c) 2011-2012, Dmitry "Divius" Tantsur
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are
#   met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following disclaimer
#     in the documentation and/or other materials provided with the
#     distribution.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#   A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#   OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#   DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#   THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#   (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os

from distutils.core import setup
from distutils.command.build import build
from distutils.command.install_data import install_data

# Detect version without importing anything

with open("pycom/constants.py", "rt") as const:
    for line in const:
        if line.startswith("__version"):
            exec(line)
    # Here we get __version__ and __version_info__

# Sphinx integration

try:
    from sphinx.setup_command import BuildDoc
    import pycom    # Sphinx will try to import it
    with_docs = True
except ImportError:
    with_docs = False
    print("Sphinx or other dependencies not found, will not build docs")

kwargs = {}

if with_docs:
    class my_install_data(install_data):

        def run(self):
            for root, dirs, files in os.walk('build/sphinx/html'):
                for fname in files:
                    fname = os.path.join(root, fname)
                    self._append_file(fname)
            return install_data.run(self)

        def _append_file(self, full_name):
            rel_name = full_name.replace("build/sphinx/html/", "")
            dir_name = os.path.dirname(rel_name)
            self.data_files.append(
                ("share/doc/pycom/html/" + dir_name, [full_name]))

    kwargs["cmdclass"] = {
        'build_sphinx': BuildDoc,
        "install_data": my_install_data
    }
    build.sub_commands.append(("build_sphinx", None))

# Setup

setup(
    name='pycom',
    version=__version__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Object Brokering',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Networking',
        'License :: OSI Approved :: BSD License'
    ],
    author="Dmitry 'Divius' Tantsur",
    author_email="divius.inside@gmail.com",
    url='http://pypi.python.org/pypi/pycom',
    description='Distributed component model for Python.',
    long_description=open("README", "rt").read(),
    license="BSD",
    requires=[
        "pyzmq (>=2.1.11)", "six"
    ],
    packages=[
        'pycom', 'pycom.apps', 'pycom.ext', 'pycom.test', 'pycom.zerojson'
    ],
    scripts=[
        'bin/pycom-nameserver'
    ],
    data_files=[
        ("share/pycom", ["bin/ns.conf"])
    ],
    **kwargs
)

#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2012 Volvox Development Team
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Author: Konstantin Lepa <konstantin.lepa@gmail.com>

import sys
import os
import re

def touch(*args):
    return open(os.path.join(*args), 'w')

prjdir = os.path.dirname(__file__)

from setuptools import setup, find_packages

from setuptools.extension import Extension
from setuptools.command.build_ext import build_ext as _build_ext
CYTHON_PYX = '_pyctpp2_py%s.cpp' % sys.version_info[0]

from distutils.version import StrictVersion

srcdir = os.path.join(prjdir, 'pyctpp2')

touch(os.path.join(srcdir, 'pyversion.pxi')).write(
    'DEF PYTHON_VERSION = %s' % sys.version_info[0]
    )

def read(filename):
    return open(os.path.join(prjdir, filename)).read()

LONG_DESC = read('README.rst') + '\nCHANGES\n=======\n\n' + read('CHANGES.rst')

oldsyspath = sys.path
sys.path.insert(0, srcdir)
from version import __version__ as VERSION
from version import CTPP2_VERSION
sys.path = oldsyspath

library_dirs = ['/usr/local/lib',
                '/usr/lib',
                '/opt/local/lib'
                ]

include_dirs = [srcdir,
                '/usr/local/include/ctpp2',
                '/usr/include/ctpp2',
                '/usr/local/include',
                '/usr/include',
                '/opt/local/include/ctpp2'
                ]

class BuildPyCTPP2(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)

        config = self.get_finalized_command('config')
        if not config.compiler:
            config.compiler = self.compiler
        if not config.check_lib('ctpp2', library_dirs=library_dirs):
            raise Exception('Failed to found ctpp2 library')

        for incdir in include_dirs:
            path = os.path.join(incdir, 'CTPP2SysHeaders.h')
            if os.path.isfile(path):
                break
        else:
            raise Exception("Failed to found CTPP2SysHeaders.h")

        p = re.compile('define\s+CTPP_VERSION\s+"(\d+\.\d+(?:.\d+)?)(?:\.[^"]*)?"')
        m = p.search(open(path).read())
        if m:
            ctpp2_version = m.group(1)
        else:
            raise Exception('Failed to check ctpp2 version.')

        required_version = '.'.join([str(v) for v in CTPP2_VERSION])
        if StrictVersion(ctpp2_version) < StrictVersion(required_version):
            raise Exception('Required ctpp2 library is %s' % required_version)

        self.run_command('config')

module = Extension(
        'pyctpp2._pyctpp2',
        [ os.path.join(srcdir, CYTHON_PYX),
          os.path.join(srcdir, 'cengine.cc'),
          os.path.join(srcdir, 'ctemplate.cc')
          ],
        language='c++',
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=['stdc++', 'ctpp2'],
        extra_compile_args=['-fno-rtti', '-fomit-frame-pointer'],
        define_macros=[('NDEBUG',)]
        )

setup(
        name='pyctpp2',
        version=VERSION,
        author="Konstantin Lepa",
        author_email="konstantin.lepa@gmail.com",
        maintainer="Konstantin Lepa",
        maintainer_email="konstantin.lepa@gmail.com",
        contact_email="konstantin.lepa@gmail.com",
        url='http://bitbucket.org/klepa/pyctpp2',
        packages=['pyctpp2'],
        license='MIT',
        description='Python interface to CTPP2 library.',
        long_description=LONG_DESC,
        cmdclass={ 'build_ext': BuildPyCTPP2 },
        ext_modules=[module],
        test_suite="tests",
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX',
            'Programming Language :: Cython',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Text Processing :: Markup :: HTML'
            ],
        requires=['Cython(>=0.14)'],
        entry_points = """
            [babel.extractors]
                ctpp2 = pyctpp2:extract_i18n_messages
            """,
    )


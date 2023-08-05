#!/usr/bin/env python

# Copyright (c) 2011 Sergey K.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


import os

from distutils.core import setup


def read_tag(tag, fname):
    with open(fname) as fp:
        for line in fp:
            if line.startswith(tag):
                return eval(line.split('=', 1)[1].strip())
        raise NameError('Missing {1} in {0}'.format(fname, tag))


def read_revision():
    try:
        import subprocess
        s = subprocess.Popen(['svn', 'info'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        s.wait()
        rev = [r for r in s.stdout.readlines() if r.startswith('Revision:')]
        return rev[0][9:].strip()
    except: pass
    return ''

this_dir = os.path.dirname(__file__)


project = 'py-rs'

version = read_tag('__version__', os.path.join(this_dir, 'rs/__init__.py'))
author = read_tag('__author__', os.path.join(this_dir, 'rs/__init__.py'))
revision = read_revision()

if revision:
    version = version+'-'+revision


classifiers = [
    'Intended Audience :: Developers',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6', 
    'Programming Language :: Python :: 2.7', 
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: WSGI',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: Libraries :: Python Modules', 
]


cmdclass = {}
command_options = {}


try:
    from sphinx.setup_command import BuildDoc

    cmdclass = {'doc' : BuildDoc}
    command_options = {
        'doc': {
            'version':('setup.py', version),
            'release':('setup.py', version),
        }
    }
except ImportError: pass


setup(name=project,
      description='Python REST framework',
      long_description=open('README').read(),
      url='http://py-rs.googlecode.com',
      version=version,
      author=author,
      author_email='py-rs@googlegroups.com',
      packages=['rs'],
      classifiers=classifiers,
      cmdclass=cmdclass,
      command_options=command_options,
      license='MIT',
      platforms='any',
)

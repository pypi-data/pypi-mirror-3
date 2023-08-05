# Copyright (C) 2011 Oren Zomer <oren.zomer@gmail.com>

#                          *** MIT License ***
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
A python library for parsing and building of data structures with the ability
of solving simple heuristics of interdepent sub-structures. It is based on
the concept of defining data structures in a declarative manner, where complex
structures are composed by combining simpler ones.
"""

import sys

if not hasattr(sys, 'version_info') or sys.version_info < (2, 6, 0, 'final'):
    raise SystemExit("pypsifas requires Python 2.6 or later.")

import os
import pickle

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from distutils.core import setup

if len(sys.argv) == 1:
    VERSION, PACKAGE_NAME, PACKAGES = pickle.load(open('setup.pkl','rb'))
    while True:
        user_answer = raw_input("Install %s%s? [y/n]\n" % (PACKAGE_NAME, VERSION)).lower()
        if user_answer in ('y', 'yes'):
            sys.argv.append('install')
            break
        elif user_answer in ('n', 'no'):
            break
        else:
            print "choose one of: y, yes, n, no"
elif sys.argv[1] == 'sdist':
    # called by bfc.setup ?
    try:
        import build_release
        build_release.build_pickle()
    except ImportError:
        pass
VERSION, PACKAGE_NAME, PACKAGES = pickle.load(open('setup.pkl','rb'))

setup(name = 'psifas',
      version = VERSION,
      author = 'Oren Zomer',
      author_email = 'oren.zomer@gmail.com',
      url = 'http://pypsifas.sourceforge.net/',
      download_url = 'http://pypsifas.sourceforge.net/',
      platforms = 'Any',
      description = __doc__.strip().split('\n')[0],
      long_description = __doc__,
      license = 'MIT',
      packages = PACKAGES,
      script_name = 'setup.py',
      )

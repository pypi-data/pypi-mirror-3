from setuptools import setup
import sys
import os

__author__ = 'Stefano Guandalini <guandalf@gmail.com>'
__version__ = '0.1.7'
__classifiers__ = [
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP',
]
__copyright__ = "2011, %s " % __author__
__license__ = """
   Copyright (C) %s

      This program is free software: you can redistribute it and/or modify
      it under the terms of the GNU General Public License as published by
      the Free Software Foundation, either version 3 of the License, or
      (at your option) any later version.

      This program is distributed in the hope that it will be useful,
      but WITHOUT ANY WARRANTY; without even the implied warranty of
      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
      GNU General Public License for more details.

      You should have received a copy of the GNU General Public License
      along with this program.  If not, see <http://www.gnu.org/licenses/>.
""" % __copyright__

__docformat__ = 'restructuredtext en'

__doc__ = """
:abstract: Python interface to Request Tracker REST API
:version: %s
:author: %s
:contact: http://stefanoguandalini.it/
:date: 2012-04-06
:copyright: %s
""" % (__version__, __author__, __license__)

wd = os.path.dirname(os.path.abspath(__file__))
os.chdir(wd)
sys.path.insert(1, wd)

name = 'python-kanbanize'

author, email = __author__.rsplit(' ', 1)
email = email.strip('<>')

version = __version__
classifiers = __classifiers__

readme = open(os.path.join(wd, 'README.rst'),'r').readlines()
print readme
description = readme[0]
long_description = ''.join(readme)

try:
    reqs = open(os.path.join(os.path.dirname(__file__), 'requirements.txt')).read()
except (IOError, OSError):
    reqs = ''

setup(
    name=name,
    version=version,
    author=author,
    author_email=email,
    url='https://github.com/guandalf/python-kanbanize',
    maintainer=author,
    maintainer_email=email,
    description=description,
    long_description=long_description,
    classifiers=classifiers,
    install_requires = reqs,
    scripts=['kanbanize.py'],
    license = 'GNU GPL',
    keywords ='kanbanize api wrapper',
    zip_safe=False,
)
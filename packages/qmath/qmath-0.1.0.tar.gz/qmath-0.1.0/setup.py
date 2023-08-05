#!/usr/bin/python
# .+
#
# .context    : Algebra
# .title      : Quaternion Algebra
# .kind	      : python source
# .author     : Marco Abrate
# .site	      : Torino - Italy
# .creation   :	10-Nov-2011
# .copyright  :	(c) 2011 Marco Abrate
# .license    : GNU General Public License
#
# qmath is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# qmath is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qmath. If not, see <http://www.gnu.org/licenses/>.
#
# .-

from distutils.core import setup
from shutil import copytree, rmtree
import os, os.path
import re
import sys

# parameters
classifiers = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License (GPL)
Programming Language :: Python
Topic :: System :: Hardware
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: POSIX :: Linux
"""


# workaround older python versions
if sys.version_info < (2, 3):
  _setup = setup
  def setup(**kwargs):
    if kwargs.has_key("classifiers"):
      del kwargs["classifiers"]
    _setup(**kwargs)

# read version string, author name, author e-mail from file
ftext = open('src/qmath.py').read()
VERSION = re.search('__version__\s+=\s+\'(\d+\.\d+\.\d+)\'',ftext).group(1)
AUTHOR = re.search('__author__ = \'([a-zA-Z]+\s+[a-zA-Z]+)\s+',ftext).group(1)
AUTHOR_EMAIL = re.search('__author__ = .*?<(.*?)>',ftext).group(1)


# do setup
setup (
  name = 'qmath',
  version = VERSION,
  author = AUTHOR,
  author_email = AUTHOR_EMAIL,
  maintainer = AUTHOR,
  maintainer_email = AUTHOR_EMAIL,
  url = 'None',
  download_url = 'None',
  license = 'http://www.gnu.org/licenses/gpl.txt',
  platforms = ['Linux'],
  description = """
  qmath provides a class for manipulating quaternion objects.
  This class provides the methods to deal algebrically with quaternions including roots evaluations and rotation representations.
  Other tools are implemented as Cross Ratio and Moebius transformations.
  """,
  classifiers = filter(None, classifiers.split("\n")),
  long_description =  """
  qmath provides a class for manipulating quaternion objects.
  This class provides the methods to deal algebrically with quaternions including roots evaluations and rotation representations.
  Other tools are implemented as Cross Ratio and Moebius transformations.
  """,
  package_dir = {'qmath':'src'},
  packages = ['qmath'])

# cleanup
if os.access('MANIFEST',os.F_OK):
  os.remove('MANIFEST')
if os.access('src.setup',os.F_OK):
  rmtree('src.setup')

#### END

# Copyright (C) 2011-2012 CRS4.
#
# This file is part of Seal.
#
# Seal is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Seal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Seal.  If not, see <http://www.gnu.org/licenses/>.

"""Seal: Sequence Alignment on Hadoop.

Seal is a of MapReduce application for biological
sequence alignment. It runs on Hadoop (http://hadoop.apache.org)
through Pydoop (http://pydoop.sourceforge.net), a Python MapReduce
and HDFS API for Hadoop.
"""

import glob
import os
import shutil
import sys
from distutils.core import setup
from distutils.errors import DistutilsSetupError

def get_arg(name):
	arg_start = "%s=" % name
	for i in xrange(len(sys.argv)):
		arg = sys.argv[i]
		if arg.startswith(arg_start):
			value = arg.replace(arg_start, "", 1)
			del sys.argv[i]
			if not value:
				raise RuntimeException("blank value specified for %s" % name)
			return value
	return None

def check_python_version():
	override = ("true" == get_arg("override_version_check"))
	if not override and sys.version_info < (2,6):
		print >>sys.stderr, "Please use a version of Python >= 2.6 (currently using vers. %s)." % ",".join( map(str, sys.version_info))
		print >>sys.stderr, "Specify setup.py override_version_check=true to override this check."
		sys.exit(1)


def get_version():
  vers = get_arg("version")
  if vers is None:
    # else, if no version specified on command line
    version_filename = os.path.join( os.path.dirname(__file__), 'VERSION')
    if os.path.exists(version_filename):
      with open(version_filename) as f:
        vers = f.read().rstrip("\n")
    else:
      from datetime import datetime
      vers = datetime.now().strftime("devel-%Y%m%d")#_%H%M%S")
  return vers

NAME = 'seal'
DESCRIPTION = __doc__.split("\n", 1)[0]
LONG_DESCRIPTION = __doc__
URL = "http://www.crs4.it"
# DOWNLOAD_URL = ""
LICENSE = 'GPL'
CLASSIFIERS = [
  "Programming Language :: Python",
  "License :: OSI Approved :: GNU General Public License (GPL)",
  "Operating System :: POSIX :: Linux",
  "Topic :: Scientific/Engineering :: Bio-Informatics",
  "Intended Audience :: Science/Research",
  ]
PLATFORMS = ["Linux"]
VERSION = get_version()
AUTHOR_INFO = [
  ("Luca Pireddu", "luca.pireddu@crs4.it"),
  ("Simone Leo", "simone.leo@crs4.it"),
  ("Gianluigi Zanetti", "gianluigi.zanetti@crs4.it"),
  ]
MAINTAINER_INFO = [
  ("Luca Pireddu", "luca.pireddu@crs4.it"),
  ]
AUTHOR = ", ".join(t[0] for t in AUTHOR_INFO)
AUTHOR_EMAIL = ", ".join("<%s>" % t[1] for t in AUTHOR_INFO)
MAINTAINER = ", ".join(t[0] for t in MAINTAINER_INFO)
MAINTAINER_EMAIL = ", ".join("<%s>" % t[1] for t in MAINTAINER_INFO)


#-- FIXME: handle internally ------------------------------------------------
from distutils.command.build import build

class seqal_build(build):
  def finalize_options(self):
    build.finalize_options(self)
    global VERSION
    # HACK!  Until we find a better way to pass a parameter 
    # into the build command.
    self.version = VERSION
    self.override_version_check = get_arg("override_version_check") or 'false'
 
  def run(self):
    build.run(self)
    libbwa_dir = "bl/lib/seq/aligner/bwa"
    libbwa_src = os.path.join(libbwa_dir, "libbwa")
    libbwa_dest = os.path.abspath(os.path.join(self.build_purelib, libbwa_dir))
    ret = os.system("BWA_LIBRARY_DIR=%s make -C %s libbwa" %
                    (libbwa_dest, libbwa_src))
    if ret:
      raise DistutilsSetupError("could not make libbwa")
    # protobuf classes
    proto_src = "bl/lib/seq/aligner/io/mapping.proto"
    ret = os.system("protoc %s --python_out=%s" %
                    (proto_src, self.build_purelib))
    if ret:
      raise DistutilsSetupError("could not run protoc")
    ret = os.system('ant -Dversion="%s" -Doverride_version_check="%s"' % (self.version, self.override_version_check))
    if ret:
      raise DistutilsSetupError("Could not build Java components")
    self.package()

  def package(self):
    dest_jar_path = os.path.join(self.build_purelib,'bl', 'seal.jar')
    if os.path.exists(dest_jar_path):
      os.remove(dest_jar_path)
    shutil.move( os.path.join(self.build_base, 'seal.jar'), dest_jar_path )



#############################################################################
# main
#############################################################################

check_python_version()
setup(name=NAME,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      url=URL,
##      download_url=DOWNLOAD_URL,
      license=LICENSE,
      classifiers=CLASSIFIERS,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      platforms=PLATFORMS,
      version=VERSION,
      packages=['bl',
                'bl.lib',
                'bl.lib.tools',
                'bl.lib.seq',
                'bl.lib.seq.aligner',
                'bl.lib.seq.aligner.bwa',
                'bl.lib.seq.aligner.io',
                'bl.mr',
                'bl.mr.lib',
                'bl.mr.seq',
                'bl.mr.seq.seqal',
                ],
      cmdclass={"build": seqal_build},
      scripts=glob.glob("bin/*"),
      )

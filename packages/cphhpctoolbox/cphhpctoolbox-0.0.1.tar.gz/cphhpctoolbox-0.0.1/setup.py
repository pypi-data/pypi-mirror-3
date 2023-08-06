#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# --- BEGIN_HEADER ---
#
# setup - setuptools install helper
# Copyright (C) 2011-2012  The cphhpc Project lead by Brian Vinter
#
# This file is part of cphhpc toolbox.
#
# Cphhpc toolbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Cphhpc toolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.
#
# -- END_HEADER ---
#

"""Setuptools install helper"""

import os
import sys
import subprocess
from setuptools import setup

# prefer local cphhpc for package and version info
sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path
from cphhpc import version_string, short_name, project_team, project_email, \
     short_desc, long_desc, project_url, download_url, license_name, \
     project_class, project_keywords, project_requires, project_extras, \
     project_platforms, maintainer_team, maintainer_email

cphhpc_lib = 'cphhpc'
core_packages = [cphhpc_lib]
for (root, dirs, files) in os.walk(cphhpc_lib):
    rel_dir = root.replace(os.path.abspath(cphhpc_lib), cphhpc_lib)
    for name in dirs:
        core_packages.append(os.path.join(rel_dir, name))
        
helper_modules = []
exec_modules = []

core_scripts = ['%s' % i for i in exec_modules]
example_scripts = []

package_list = core_packages

# Distro packaging name
install_name = "python-%s" % short_name
setup(name=short_name,
      version=version_string,
      description=short_desc,
      long_description=long_desc,
      author=project_team,
      author_email=project_email,
      maintainer=maintainer_team,
      maintainer_email=maintainer_email,
      url=project_url,
      download_url=download_url,
      license=license_name,
      classifiers=project_class,
      keywords=project_keywords,
      platforms=project_platforms,
      install_requires=project_requires,
      requires=project_requires,
      extras_require=project_extras,
      packages=package_list,
      scripts=core_scripts
      )

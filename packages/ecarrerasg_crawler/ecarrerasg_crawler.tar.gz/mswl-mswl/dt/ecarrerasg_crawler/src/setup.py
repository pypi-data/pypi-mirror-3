#!/usr/bin/env python
#
#    Copyright (c) 2011 Esteban Carreras Genis. All rights reserved.
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from setuptools import setup, find_packages

setup ( name = "ecarrerasg_crawler",
version = "0.1",
packages = find_packages (),
scripts = [ 'ecarrerasg_crawler'] ,
install_requires = [ 'BeatifulSoup'],
package_data = { 'pyecarrerasg_crawler': [''],},
author = " Esteban Carreras ",
author_email = "ecarrerasg@gmail.com",
description = " Web Crawler ",
license = "GPLv3",
keywords = "",
url = "http://code.sidelab.es/projects/estebancarreras/files",
long_description = "ecarrerasg_crawler. This is a project of the subject Development Tools of Master in Free Software",
download_url = "https://gitorious.org/mswl/mswl/trees/master/",)


# Copyright (C) 2012  Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

setup(
    name="pkgme-service-python",
    version="0.3",
    author="Canonical Consumer Applications",
    author_email="canonical-consumer-applications@lists.launchpad.net",
    license="GPL3",
    install_requires=[
        "piston-mini-client",
        ],
    zip_safe=False,
    packages=find_packages('.'),
)

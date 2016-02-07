# ##### BEGIN GPL LICENSE BLOCK #####
#
# Part of the Cycles sub-package of Blib.
# Cycles Blib version: Version info for the Cycles sub-package of Blib.
# Copyright (C) 2016  Luca Rood
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

"""
Version control for Cycles (Blib) package.

Attributes:
    version (blib.utils.Version): Version of this release.
    compatible (blib.utils.Version): Earliest release with which this one is compatible.
"""

from ..utils import Version

version = Version("0.1.0", "beta")
compatible = Version("0.1.0", "beta")

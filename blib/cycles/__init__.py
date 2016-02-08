# ##### BEGIN GPL LICENSE BLOCK #####
#
# Part of the Blib package.
# Cycles Blib package: Cycles export/import as per the Blib standard.
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

"""Cycles export/import as per the Blib standard."""

from .bexport import bexport
from .bimport import bimport
from .generate_xml import generate_xml
from .version import version as ver

__all__ = ["bexport", "bimport", "generate_xml"]
__version__ = ver.decorated
__author__ = 'Luca Rood'

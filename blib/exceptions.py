# ##### BEGIN GPL LICENSE BLOCK #####
#
# Part of the Blib package.
# Blib exceptions: Generic Blib exceptions.
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

"""Generic Blib exceptions, independent of specific sub-packages."""

class BlibException(Exception):
    """
    Blib base exception, should never be raised.
    Should be the base class for any blib exception, even sub-package specific exceptions.
    Only use to sub-class exceptions, or to catch any Blib exception.
    """
    pass

class InvalidBlibFile(BlibException):
    """Raised when the passed file is not a Blib file, or is broken."""
    pass

class BlibVersionError(BlibException):
    """Raised when the passed file was created with a later, backwards incompatible version of Blib."""
    pass

class BlibTypeError(BlibException):
    """Raised when the .blib file is not of the correct type for the operation."""
    pass

class InvalidObject(BlibException):
    """Raised when the passed object, is not compatible with that exporter."""
    pass

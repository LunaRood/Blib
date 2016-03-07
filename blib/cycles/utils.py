# ##### BEGIN GPL LICENSE BLOCK #####
#
# Cycles import/export: Cycles IO using the Blib package.
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

import bpy

from ..exceptions import InvalidObject

def check_asset(asset, do_raise=False):
    """
    Check if asset is a Cycles material or node group,
    and thus is exportable by the 'cycles' package.
    
    Args:
        asset (any type): Asset to be checked for validity.
        do_raise (bool): If True, an exception is raised for invalid assets,
            instead of returning False.
    
    Returns:
        bool: True if check is passed, otherwise returns False.
        Note that False is only ever returned if 'do_raise' is False,
        otherwise an exception is raised instead.
    
    Raises:
        blib.exeptions.InvalidObject: If the check fails and 'do_raise' is True.
    """
    
    if asset:
        if isinstance(asset, bpy.types.Material):
            if asset.use_nodes:
                tree = asset.node_tree
            else:
                if do_raise:
                    raise InvalidObject("Material can't be exported, contains no node tree.")
                else:
                    return False
        elif isinstance(asset, bpy.types.ShaderNodeTree):
            if asset.type == 'SHADER':
                tree = asset
            else:
                if do_raise:
                    raise InvalidObject("Node tree is not of SHADER type.")
                else:
                    return False
        else:
            if do_raise:
                raise InvalidObject("Object passed is not a material or node group.")
            else:
                return False
        
        groups = [tree]
        while groups:
            for node in groups.pop(0).nodes:
                if 'NEW_SHADING' not in node.shading_compatibility:
                    if do_raise:
                        raise InvalidObject("Node tree contains non Cycles nodes.")
                    else:
                        return False
                
                if node.bl_static_type == 'GROUP':
                    groups.append(node.node_tree)
    return True

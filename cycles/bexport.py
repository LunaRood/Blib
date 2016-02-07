# ##### BEGIN GPL LICENSE BLOCK #####
#
# Part of the Cycles sub-package of Blib.
# Cycles Blib export: Exports Blender Cycles material or node group.
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

import re
import zipfile as zf
from os import path, listdir
from io import BytesIO
from binascii import crc32

from .version import version, compatible
from .generate_xml import generate_xml
from ..utils import files_equal, archive_sha1, gen_crc
from ..exceptions import InvalidObject

def file_int(f):
    return int(re.sub(r".*?([0-9]+)$", r"\1", f))

def find_range(files, val, lower):
    low = 0
    high = len(files) - 1
    while files[low] <= val and files[high] >= val:
        if low == high:
            mid = low
        else:
            mid = low + ((val - files[low]) * (high - low)) // (files[high] - files[low])
        
        val = files[mid]
        if files[mid] < val:
            low = mid + 1
        elif files[mid] > val:
            high = mid - 1
        else:
            return mid
    
    if lower:
        if val < files[0]:
            return 0
        else:
            if files[mid] > val:
                return mid
            else:
                return mid + 1
    else:
        if val > files[-1]:
            return len(files) - 1
        else:
            if files[mid] < val:
                return mid
            else:
                return mid - 1

def write_img(archive, source, destination, crcs, packed):
    crc = crc32(source) if packed else gen_crc(source)
    if crc in crcs:
        for zpath in crcs[crc]:
            zimg = archive.open(zpath, 'r')
            nimg = BytesIO(source) if packed else open(source, 'rb')
            if files_equal(zimg, nimg):
                archive.writestr(destination, b"")
                archive.getinfo(destination).comment = zpath.encode("utf-8")
                zimg.close()
                nimg.close()
                break
            zimg.close()
            nimg.close()
        else:
            archive.writestr(destination, source) if packed else archive.write(source, destination)
            crcs[crc].append(destination)
    else:
        archive.writestr(destination, source) if packed else archive.write(source, destination)
        crcs[crc] = [destination]

def bexport(object, filepath, imgi_export=True, imge_export=True, seq_export=True, mov_export=True,
        txti_export=True, txte_export=True, script_export=True, optimize_file=False, compress=True):
    """
    Export a Cycles material or node group to a .blib file.
    
    Args:
        object (bpy.types.Material or bpy.types.ShaderNodeTree): The object to be exported,
            has to be Cycles object, no other renderers supported.
        filepath (str): Path to save the file.
        imgi_export (bool): Export images that are packed in .blend file.
        imge_export (bool): Export images that are externally saved.
        seq_export (bool): Export image sequences.
        mov_export (bool): Export movies.
        txti_export (bool): Export texts that are packed in .blend file.
        txte_export (bool): Export texts that are externally saved.
        script_export (bool): Export scripts that are referenced by path in "script" node.
        optimize_file (bool): Optimize file, by not including variables qual to None or "".
        compress (bool): Use compression on the zip container.
    
    Raises:
        blib.exeptions.InvalidObject: If the object argument is not a Cycles material or node tree.
    """
    
    if isinstance(object, bpy.types.Material):
        if object.use_nodes == False:
            raise InvalidObject("Material can't be exported, contains no node tree.")
    elif isinstance(object, bpy.types.ShaderNodeTree):
        raise InvalidObject("Object passed is not a material or node group")
    
    filepath = bpy.path.abspath(filepath) #Ensure path is absolute
    xml, imgs, txts = generate_xml(object, imgi_export, imge_export, seq_export, mov_export, txti_export,
                                   txte_export, script_export, optimize_file, True, False, False) #Generate XML
    compression = zf.ZIP_DEFLATED if compress else zf.ZIP_STORED
    archive = zf.ZipFile(filepath, 'w', compression) #Create archive
    archive.writestr('structure.xml', xml) #Write XML to archive
    
    #Write text files to archive
    for txt in txts:
        if "text" in txt:
            archive.writestr(txt["destination"], txt["text"].as_string().encode("utf-8"))
        else:
            archive.write(txt["source"], txt["destination"])
    
    #Write images to archive
    crcs = {}
    for img in imgs:
        if img["image"].source == 'SEQUENCE':
            ### Image sequence code
            p, f = path.split(bpy.path.abspath(img["image"].filepath))
            n, e = path.splitext(f)
            base = re.sub(r"[0-9]+$", "", n)
            files = [path.splitext(fil)[0] for fil in listdir(p) if path.isfile(path.join(p, fil)) and \
                     re.match(r"^" + re.escape(base) + r"[0-9]+" + re.escape(e) + r"$", fil)]
            files.sort(key=file_int)
            files_int = [file_int(fil) for fil in files]
            start = find_range(files_int, img["range"][0], True)
            end = find_range(files_int, img["range"][1], False)
            for i in range(start, end + 1):
                source = path.join(p, files[i] + e)
                destination = img["destination"] + "/" + files[i] + e
                write_img(archive, source, destination, crcs, False)
            
            if not img["destination"] + "/" + bpy.path.basename(img["image"].filepath) in archive.namelist():
                source = bpy.path.abspath(img["image"].filepath)
                destination = img["destination"] + "/" + bpy.path.basename(img["image"].filepath)
                write_img(archive, source, destination, crcs, False)
        else:
            if img["image"].packed_file is None:
                source = bpy.path.abspath(img["image"].filepath)
                destination = img["destination"]
                write_img(archive, source, destination, crcs, False)
            else:
                source = img["image"].packed_file.data
                destination = img["destination"]
                write_img(archive, source, destination, crcs, True)
    
    checksum = archive_sha1(archive)
    
    comment = checksum.hexdigest() + " cycles " + str(version) + " " + str(compatible)
    
    archive.comment = comment.encode("utf-8")
    
    archive.close()

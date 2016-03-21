# ##### BEGIN GPL LICENSE BLOCK #####
#
# Part of the Blib package.
# Blib utilities: Common Blib functions and classes.
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

"""Utility classes and functions for Blib packages."""

import zipfile as zf
from binascii import crc32
from hashlib import sha1
from os import path, makedirs, listdir
from shutil import copyfileobj
from io import BytesIO

class Version(object):
    """
    Version control object.
    
    Creates multi-part version number functionality.
    Using str(instance) returns a string containing dot separated numbers.
    
    Args:
        version (str): Dot separated integer string (e.g. "1.0.2")
        rel_type (str): Release type (e.g. "beta", "stable", etc.).
            Used to generate decorated string, for display purposes.
    
    Attributes:
        decorated (str): Decorated string, in format "<dot separated version number> (<rel_type>)" (e.g. "1.0.2 (stable)").
    """
    
    def __init__(self, version, rel_type=None):
        self._parts = [int(part) for part in version.split(".")]
        self._str = version
        self._type = rel_type
    
    def __repr__(self):
        return str(self._parts)
    
    def __str__(self):
        return self._str
    
    def __eq__(self, other):
        ver1 = self._parts
        ver2 = other._parts
        return ver1 == ver2
    
    def __ne__(self, other):
        ver1 = self._parts
        ver2 = other._parts
        return ver1 != ver2
    
    def __gt__(self, other):
        ver1 = self._parts
        ver2 = other._parts
        for pair in zip(ver1, ver2):
            if pair[0] > pair[1]:
                return True
            elif pair[0] < pair[1]:
                return False
        if len(ver1) > len(ver2):
            return True
        else:
            return False
    
    def __lt__(self, other):
        ver1 = self._parts
        ver2 = other._parts
        for pair in zip(ver1, ver2):
            if pair[0] < pair[1]:
                return True
            elif pair[0] > pair[1]:
                return False
        if len(ver1) < len(ver2):
            return True
        else:
            return False
    
    def __ge__(self, other):
        ver1 = self._parts
        ver2 = other._parts
        for pair in zip(ver1, ver2):
            if pair[0] > pair[1]:
                return True
            elif pair[0] < pair[1]:
                return False
        if len(ver1) >= len(ver2):
            return True
        else:
            return False
    
    def __le__(self, other):
        ver1 = self._parts
        ver2 = other._parts
        for pair in zip(ver1, ver2):
            if pair[0] < pair[1]:
                return True
            elif pair[0] > pair[1]:
                return False
        if len(ver1) <= len(ver2):
            return True
        else:
            return False
    
    @property
    def decorated(self):
        if self._type is not None:
            return self._str + " ({})".format(self._type)
        else:
            return self._str

class ResourceDir(object):
    """
    Keeps initialized path available, but only creates directory when the path is requested.
    
    Using str(instance) will create the directory (if necessary), and return the path.
    
    When truth checking an instance, it will be True only if the path has been requested
    and thus the directory created, otherwise it is False.
    
    Args:
        name (str): Name of the resource type.
        directory (str or None): Path to resource directory.
    
    Attributes:
        root (read-only[str]): Path to the root directory for the resource type.
    """
    
    def __init__(self, name, directory=None):
        self._name = name
        self._path = None
        if directory is None:
            self._root = path.join(gen_resource_path(), name)
        else:
            self._root = path.join(directory, name)
    def __repr__(self):
        if self._path is not None:
            return "'{}'".format(self._path)
        else:
            return None
    def __str__(self):
        self._make()
        return self._path
    
    def __bool__(self):
        if self._path:
            return True
        else:
            return False
    
    @property
    def root(self):
        return self._root
    
    @root.setter
    def root(self, val):
        raise AttributeError("'ResourceDir' object attribute 'root' is read-only")
    
    @root.deleter
    def root(self):
        raise AttributeError("'ResourceDir' object attribute 'root' is read-only")
    
    def _make(self):
        if self._path is None:
            if self._name == "tmp":
                self._path = self._root
            else:
                if path.isdir(self._root):
                    dir_list = [int(d) for d in listdir(self._root) if path.isdir(path.join(self._root, d)) and is_int(d)]
                    dir_list.sort()
                    dir_name = str(dir_list[-1] + 1)
                    self._path = path.join(self._root, dir_name)
                else:
                    self._path = path.join(self._root, "1")
            if not path.isdir(self._path):
                makedirs(self._path)

def get_path(archive, item):
    """
    Resolve reference chain.
    
    Args:
        archive (zipfile.ZipFile): The archive wherein the file is located.
        item (str): The path to the item inside the archive.
    
    Returns:
        str: Path to the file within the archive.
    """
    
    fpath = item
    while True:
        comment = archive.getinfo(fpath).comment.decode("utf-8")
        if comment == "":
            break
        else:
            fpath = comment
    return fpath

def extract(archive, item, directory):
    """
    Extract item from ZIP archive, without keeping internal ZIP structure, and resolving references.
    
    Args:
        archive (zipfile.ZipFile): The archive from which to extract the item.
        item (str): The path to the item inside the archive.
        directory (str): The path to the directory to which to extract.
    
    Returns:
        str: Path to the extracted file.
    """
    
    d_path = path.join(directory, path.basename(item))
    s_path = get_path(archive, item)
    src = archive.open(s_path, 'r')
    dst = open(d_path, 'wb')
    copyfileobj(src, dst)
    src.close()
    dst.close()
    return d_path

def fail(failed, f_type, action):
    """
    Increment fail counter and print fail to console.
    
    Args:
        failed (dict): Dictionary of fail counters.
        f_type (str): The type of fail occurred (must be same as corresponding key in failed dict).
        action (str): Action that failed (e.g. "import", "export", "link"...)
        name (str): Name of the object on which the action failed.
        reason (str): Reason for which the action failed (e.g. "a <some resource> is missing")
    """
    failed.setdefault(f_type, 0)
    failed[f_type] += 1
    print("Failed to {}.".format(action))

def files_equal(file1, file2):
    """
    Check if files contain same data.
    
    Args:
        file1, file2 (file object): Files should be loaded in the same mode (i.e. binary or text),
            otherwise equal files may seem different.
    
    Returns:
        bool
    """
    
    while True:
        data1 = file1.read(1024)
        data2 = file2.read(1024)
        
        if data1 != data2:
            return False
        
        if not data1 and not data2:
            return True

def archive_sha1(archive):
    """
    Generate sha1 hash from crc32 hashes of all files in archive.
    
    Args:
        archive (zipfile.ZipFile): The archive for which to generate the hash.
    
    Returns:
        hashlib.sha1: The resulting hash object.
    """
    
    checksum = sha1()
    for obj in archive.infolist():
        checksum.update(bytes([int(i) for i in str(obj.CRC)]))
    return checksum

def gen_crc(filepath):
    """
    Generate crc32 hash, without loading whole file to disk.
    
    Args:
        filepath (str): Path to file to be hashed.
    
    Returns:
        int: crc32 hash in decimal form.
    """
    
    f = open(filepath, 'rb')
    crc = crc32(b"")
    while True:
        data = f.read(1024)
        if data:
            crc = crc32(data, crc)
        else:
            break
    f.close()
    return crc

def write(archive, source, destination, crcs):
    """
    Write data to archive, while only making a link if identical data is already in archive.
    
    Args:
        archive (zipfile.ZipFile): The archive to which to write the data.
        source (str or bytes): The path to the file to be written or the data itself.
            If source is 'str', it is interpreted as a file path.
            If source is 'bytes', it is interpreted as data to be written directly.
        destination (str): The path within the archive to which the data should written.
        crcs (dict): A dictionary containing crc32 hashes to all files in archive.
            Can be passed as an empty dictionary.
            Same dict should be passed every time you write to the same archive.
    
    Raises:
        TypeError: If the 'source' argument is not a 'str' or 'bytes' object.
    """
    
    if isinstance(source, str):
        is_file = True
    elif isinstance(source, bytes):
        is_file = False
    else:
        raise TypeError("source should be of type 'str' or 'bytes', not '{}'".format(type(source).__name__))
    
    crc = gen_crc(source) if is_file else crc32(source)
    if crc in crcs:
        for zpath in crcs[crc]:
            zfile = archive.open(zpath, 'r')
            nfile = open(source, 'rb') if is_file else BytesIO(source)
            if files_equal(zfile, nfile):
                archive.writestr(destination, b"")
                archive.getinfo(destination).comment = zpath.encode("utf-8")
                zfile.close()
                nfile.close()
                break
            zfile.close()
            nfile.close()
        else:
            archive.write(source, destination) if is_file else archive.writestr(destination, source)
            crcs[crc].append(destination)
    else:
        archive.write(source, destination) if is_file else archive.writestr(destination, source)
        crcs[crc] = [destination]

def is_int(string):
    """
    Check if string is integer (strict check).
    
    Args:
        string (str): string to be checked
    
    Returns:
        bool
    """
    
    try:
        int(string)
    except ValueError:
        return False
    else:
        return True

def gen_resource_path():
    """
    Generate path to resources relative to the module path.
    
    Returns:
        str: "<module directory>/resources"
    """
    
    res_path = path.dirname(path.abspath(__file__))
    res_path = path.join(res_path, "resources")
    return res_path

def get_file_type(f_path):
    """
    Get the Blib type of a file.
    
    Args:
        f_path (str): Path to the file to be checked.
    
    Returns:
        str or None
        A string containing the Blib type is returned,
        if no valid type is found, None is returned.
    """
    
    try:
        archive = zf.ZipFile(f_path, 'r')
    except zf.BadZipFile:
        return None
    
    try:
        blib_type = archive.comment.decode("utf-8").split(" ")[1]
    except ValueError:
        return None
    
    archive.close()
    return blib_type

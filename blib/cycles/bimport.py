# ##### BEGIN GPL LICENSE BLOCK #####
#
# Part of the Cycles sub-package of Blib.
# Cycles Blib import: Imports Blender Cycles material or node group.
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
import xml.etree.cElementTree as ET
from ast import literal_eval as parse
from os import path, listdir, makedirs, remove
from shutil import copyfile, rmtree

from .version import version
from ..utils import files_equal, archive_sha1, fail, extract, get_path
from ..utils import Version, ResourceDir
from ..exceptions import InvalidBlibFile, BlibVersionError, BlibTypeError

def extract_image(archive, source, destination, path_dict, failed):
    try:
        ipath = extract(archive, source, destination)
    except KeyError:
        fail(failed, "images", "import image '{}', file is missing".format(source))
        return None
    else:
        path_dict[source] = ipath
        return ipath

def import_texts(orig, dest, xtxt, txts, failed, archive, txt_dir, txt_paths=None):
    if orig == "xml": #From XML
        if dest == "ext": #To external
            tpath = path.join(str(txt_dir), xtxt.attrib["name"])
            tfile = open(tpath, 'w', encoding="utf-8")
            tfile.write(xtxt.text)
            tfile.close()
            try:
                txt = bpy.data.texts.load(tpath)
            except:
                fail(failed, "texts", "import text '{}', unknown reason".format(xtxt.attrib["name"]))
            else:
                txts[xtxt.attrib["name"]] = txt
                if txt_paths is not None:
                    txt_paths[xtxt.attrib["path"]] = tpath
        
        elif dest == "int": #To internal
            txt = bpy.data.texts.new(xtxt.attrib["name"])
            try:
                txt.from_string(xtxt.text)
            except:
                bpy.data.texts.remove(txt)
                fail(failed, "texts", "import text '{}', unknown reason".format(xtxt.attrib["name"]))
            else:
                txts[xtxt.attrib["name"]] = txt
                if txt_paths is not None:
                    txt_paths[xtxt.attrib["path"]] = txt
    
    elif orig == "zip": #From Zip
        if dest == "ext":  #To external
            try:
                tpath = extract(archive, xtxt.attrib["path"], str(txt_dir))
            except KeyError:
                fail(failed, "texts", "import text '{}', file is missing".format(xtxt.attrib["name"]))
            else:
                try:
                    txt = bpy.data.texts.load(tpath)
                except:
                    fail(failed, "texts", "import text '{}', unknown reason".format(xtxt.attrib["name"]))
                else:
                    txts[xtxt.attrib["name"]] = txt
                    if txt_paths is not None:
                        txt_paths[xtxt.attrib["path"]] = tpath
        
        elif dest == "int": #To internal
            tpath = get_path(archive, xtxt.attrib["path"])
            try:
                tfile = archive.open(tpath, 'r')
            except KeyError:
                fail(failed, "texts", "import text '{}', file is missing".format(xtxt.attrib["name"]))
            else:
                txt = bpy.data.texts.new(xtxt.attrib["name"])
                try:
                    txt.from_string(tfile.read().decode("utf-8"))
                except:
                    bpy.data.texts.remove(txt)
                    fail(failed, "texts", "import text '{}', unknown reason".format(xtxt.attrib["name"]))
                else:
                    txts[xtxt.attrib["name"]] = txt
                    if txt_paths is not None:
                        txt_paths[xtxt.attrib["path"]] = txt
                tfile.close()

def set_attributes(object, xelement, failed):
    for attr in xelement.attrib:
        if not attr.startswith("blib_") and \
           not (attr == "name" and isinstance(object, bpy.types.Material)) and \
           not (attr == "mode" and isinstance(object, bpy.types.ShaderNodeScript)):
            try:
                val = parse(xelement.attrib[attr])
            except (ValueError, SyntaxError):
                val = xelement.attrib[attr]
            
            try:
                setattr(object, attr, val)
            except:
                fail(failed, "attributes", "set attribute '{}' on object '{}'".format(attr, object.name))

def make_sockets(tree, inp, out, xinpn, xoutn):
    types = ('VALUE', 'INT', 'BOOLEAN', 'VECTOR', 'STRING', 'RGBA', 'SHADER')
    routes = {}
    outs = {}
    
    for i, ty in enumerate(types):
        route = tree.nodes.new("NodeReroute")
        routes[ty] = route
        link = tree.links.new(inp.outputs[i], route.inputs[0])
        tree.links.remove(link)
        inp.outputs[i].type = ty
        link = tree.links.new(inp.outputs[i], route.inputs[0])
        if ty == "VECTOR":
            route.inputs[0].hide_value = True
        link2 = tree.links.new(inp.outputs[i + 1], routes[ty].inputs[0])
        tree.inputs.remove(tree.inputs[i])
        outs[ty] = inp.outputs[i]
    
    if xinpn is not None:
        xouts = xinpn.find("outputs")
        if xouts is not None:
            for i, xout in enumerate(xouts):
                tree.links.new(inp.outputs[i + 7], routes[xout.attrib["type"]].inputs[0])
                tree.links.new(outs[xout.attrib["type"]], routes[xout.attrib["type"]].inputs[0])
                tree.inputs[i + 7].name = xout.attrib["name"]
    
    if xoutn is not None:
        xinps = xoutn.find("inputs")
        if xinps is not None:
            for i, xinp in enumerate(xinps):
                link = tree.links.new(outs[xinp.attrib["type"]], out.inputs[i])
                tree.outputs[i].name = xinp.attrib["name"]
    
    for route in routes.values():
        tree.nodes.remove(route)
        tree.inputs.remove(tree.inputs[0])

def set_grp_io(xinp, xout, inp, out, tree):
    if xinp is not None or xout is not None:
        inp = tree.nodes.new("NodeGroupInput") if inp is None else inp
        make_sockets(tree, inp, out, xinp, xout)
        if xinp is None:
            tree.nodes.remove(inp)

def build_tree(xnodes, xlinks, tree, resources, txt_embed, txt_dir, blib, script_import, archive, failed):
    imgs = resources["images"]
    txts = resources["texts"]
    txt_paths = resources["text_paths"]
    scripts = resources["scripts"]
    grps = resources["groups"]
    xinp = None
    xout = None
    inp = None
    out = None
    nodes = {}
    
    for n_i, xnode in enumerate(xnodes):
        node = tree.nodes.new(xnode.attrib["bl_idname"])
        if node.type == 'GROUP' and "blib_node_tree" in xnode.attrib:
            node.node_tree = grps[xnode.attrib["blib_node_tree"]]
        elif node.type == 'SCRIPT':
            if xnode.attrib["mode"] == 'INTERNAL':
                node.mode = 'INTERNAL'
                if "blib_script" in xnode.attrib:
                    scr = xnode.attrib["blib_script"]
                    if scr in txts:
                        node.script = txts[scr]
            else:
                if blib and script_import and "blib_filepath" in xnode.attrib:
                    blib_path = xnode.attrib["blib_filepath"]
                    if txt_embed == True:
                        node.mode = 'INTERNAL'
                        if blib_path in scripts:
                            node.script = scripts[blib_path]
                        elif blib_path in txt_paths:
                            node.script = txt_paths[blib_path]
                            scripts[blib_path] = txt_paths[blib_path]
                        else:
                            spath = get_path(archive, xnode.attrib["blib_filepath"])
                            try:
                                sfile = archive.open(spath, 'r')
                            except KeyError:
                                fail(failed, "scripts", "import script '{}', file is missing".format(blib_path))
                            else:
                                script = bpy.data.texts.new(bpy.path.basename(blib_path))
                                try:
                                    script.from_string(sfile.read().decode("utf-8"))
                                except:
                                    bpy.data.texts.remove(script)
                                    fail(failed, "scripts", "import script '{}', unknown reason".format(blib_path))
                                else:
                                    scripts[blib_path] = script
                                    node.script = script
                                sfile.close()
                    else:
                        node.mode = 'EXTERNAL'
                        if blib_path in scripts:
                            node.filepath = scripts[blib_path]
                        elif blib_path in txt_paths:
                            node.filepath = txt_paths[blib_path]
                            scripts[blib_path] = txt_paths[blib_path]
                        else:
                            try:
                                spath = extract(archive, blib_path, str(txt_dir))
                            except KeyError:
                                fail(failed, "scripts", "import script '{}', file is missing".format(blib_path))
                            else:
                                scripts[blib_path] = spath
                                node.filepath = spath
        elif node.type == 'FRAME':
            if "blib_text" in xnode.attrib:
                txt = xnode.attrib["blib_text"]
                if txt in txts:
                    node.text = txts[txt]
        elif node.type == 'GROUP_INPUT':
            xinp = xnode
            inp = node
        elif node.type == 'GROUP_OUTPUT':
            xout = xnode
            out = node
        elif hasattr(node, "image_user"):
            if "blib_image" in xnode.attrib:
                img = xnode.attrib["blib_image"]
                if img in imgs:
                    node.image = imgs[img]
                ximageuser = xnode.find("image_user")
                set_attributes(node.image_user, ximageuser, failed)
        elif hasattr(node, "mapping") and hasattr(node.mapping, "curves"):
            xcurvedata = xnode.find("curve_data")
            curvedata = parse(xcurvedata.text)
            for c_i, curve in enumerate(curvedata):
                for p_i, point in enumerate(curve):
                    if p_i == 0 or p_i == len(curve) - 1:
                        node.mapping.curves[c_i].points[p_i].location = point[0]
                        node.mapping.curves[c_i].points[p_i].handle_type = point[1]
                    else:
                        node.mapping.curves[c_i].points.new(point[0][0], point[0][1])
                        node.mapping.curves[c_i].points[p_i].handle_type = point[1]
            node.mapping.update()
        elif hasattr(node, "color_ramp"):
            xrampdata = xnode.find("ramp_data")
            rampdata = parse(xrampdata.text)
            set_attributes(node.color_ramp, xrampdata, failed)
            for e_i, element in enumerate(rampdata):
                if e_i == 0 or e_i == len(rampdata) - 1:
                    node.color_ramp.elements[e_i].position = element[0]
                    node.color_ramp.elements[e_i].color = element[1]
                else:
                    node.color_ramp.elements.new(element[0])
                    node.color_ramp.elements[e_i].color = element[1]
        nodes[xnode.attrib["name"]] = node
    
    set_grp_io(xinp, xout, inp, out, tree)
    
    if xlinks is not None:
        for xlink in xlinks:
            n_from = nodes[xlink.attrib["from_node"]]
            n_to = nodes[xlink.attrib["to_node"]]
            s_from = int(xlink.attrib["from_socket"])
            s_to = int(xlink.attrib["to_socket"])
            try:
                tree.links.new(n_from.outputs[s_from], n_to.inputs[s_to])
            except IndexError:
                s_nodes = []
                if (s_from >= len(n_from.outputs) and n_from.type == 'SCRIPT' and
                   ((n_from.mode == 'EXTERNAL' and n_from.filepath == "") or (n_from.mode == 'INTERNAL' and n_from.script is None))):
                    s_nodes.append(("from", n_from.name))
                
                if (s_to >= len(n_to.inputs) and n_to.type == 'SCRIPT' and
                   ((n_to.mode == 'EXTERNAL' and n_to.filepath == "") or (n_to.mode == 'INTERNAL' and n_to.script is None))):
                    s_nodes.append(("to", n_to.name))
                
                if len(s_nodes) > 0:
                    for s_node in s_nodes:
                        fail(failed, "links", "link {} '{}', because an OSL script is missing".format(s_node[0], s_node[1]))
                else:
                    raise
    
    for xnode in xnodes:
        node = nodes[xnode.attrib["name"]]
        
        if "blib_parent" in xnode.attrib:
            node.parent = nodes[xnode.attrib["blib_parent"]]
        
        set_attributes(node, xnode, failed)
        
        xinps = xnode.find("inputs")
        xouts = xnode.find("outputs")
        
        if xinps is not None:
            for i_i, xinp in enumerate(xinps):
                set_attributes(node.inputs[i_i], xinp, failed)
        
        if xouts is not None:
            for o_i, xout in enumerate(xouts):
                set_attributes(node.outputs[o_i], xout, failed)

def bimport(filepath, resource_path=None, imgi_import=True, imge_import=True, seq_import=True, mov_import=True, txti_import=True, txte_import=True,
            script_import=True, img_embed=False, txt_embed=None, skip_sha1=False, img_merge=True):
    """
    Import a Cycles material or node group from a .blib or .xml file.
    
    Args:
        filepath (str): Path to .blib or .xml file.
        resource_path (str or None): Custom path to save external resources or None to keep the default path.
        imgi_import (bool): Import images that were packed in .blend file.
        imge_import (bool): Import images that were externally saved.
        seq_import (bool): Import image sequences.
        mov_import (bool): Import movies.
        txti_import (bool): Import texts that were packed in .blend file.
        txte_import (bool): Import texts that were externally saved.
        script_import (bool): Import scripts that were referenced by path in "script" node.
        img_embed (bool or None): Pack images. True to pack, False to save externally,
            and None to keep the setup from the exported material.
        txt_embed (bool or None): Pack texts. True to pack, False to save externally,
            and None to keep the setup from the exported material.
        skip_sha1 (bool): Skip checksum verification. Allows the importing of manually edited
            materials, that would otherwise seem corrupted (use with caution).
        img_merge (bool): If an image contained in the .blib, is already available in the local
            resources, use the existing image instead of creating a new instance.
    
    Returns:
        bpy.types.Material or bpy.types.ShaderNodeTree
        The produced material or node tree.
    
    Raises:
        blib.exeptions.InvalidBlibFile: If the file is not a valid Blender Library.
        blib.exeptions.BlibTypeError: If the Blender Library is not of type "cycles".
        blib.exeptions.BlibVersionError: If the file was created with a later, backwards incompatible version of Blib.
    """
    
    filepath = bpy.path.abspath(filepath) #Ensure path is absolute
    
    if resource_path is None or resource_path.strip() == "":
        resource_path = None
    else:
        resource_path = bpy.path.abspath(resource_path) #Ensure path is absolute
    
    if path.splitext(filepath)[1] == ".blib":
        try:
            archive = zf.ZipFile(filepath, 'r')
        except zf.BadZipFile:
            raise InvalidBlibFile("File is not a valid Blender library")
        
        blib = True
        try:
            file_checksum, blibtype, file_version, compatible, *rest = archive.comment.decode("utf-8").split(" ")
        except ValueError:
            raise InvalidBlibFile("File is broken, missing meta-data")
        
        compatible = Version(compatible)
        
        if blibtype == "cycles":
            if compatible <= version:
                if archive.testzip() is not None:
                    raise InvalidBlibFile("File is broken")
                else:
                    if not skip_sha1:
                        checksum = archive_sha1(archive)
                        
                        if not file_checksum == checksum.hexdigest():
                            raise InvalidBlibFile("Checksum does not match, file may be broken or have been altered\n"
                                                  'Run with "skip_sha1" to ignore checksum')
            else:
                raise BlibVersionError("File has incompatible version of blib")
        else:
            raise BlibTypeError("File is not a valid Cycles material")
        try:
            xml_file = archive.open("structure.xml", 'r')
        except KeyError:
            raise InvalidBlibFile("File is broken, missing structure XML")
        tree = ET.ElementTree(file=xml_file)
        xml_file.close()
        xroot = tree.getroot()
    
    elif path.splitext(filepath)[1] == ".xml":
        tree = ET.ElementTree(file=filepath)
        xroot = tree.getroot()
        blib = False
        xversion = Version(xroot.attrib["compatible"])
        if xversion > version:
            raise BlibVersionError("File has incompatible version of blib")
    
    else:
        raise InvalidBlibFile("File is not a Blender library")
    
    if xroot.tag != "blib":
        raise InvalidBlibFile("File is not a Blender library")
    
    if xroot.attrib["type"] != "cycles":
        raise BlibTypeError("File is not a valid Cycles material")
    
    failed = {}
    imgs = {}
    txts = {}
    txt_paths = {}
    grps = {}
    scripts = {}
    resources = {
        "images": imgs,
        "texts": txts,
        "text_paths": txt_paths,
        "groups": grps,
        "scripts": scripts,
    }
    txt_dir = ResourceDir("texts", resource_path)
    xres = xroot.find("resources")
    
    #Import resources
    if xres is not None:
        ximgs = xres.find("images")
        xtxts = xres.find("texts")
        xgrps = xres.find("groups")
        tmp_path = ResourceDir("tmp", resource_path)
        path_dict = {}
        
        #Images
        if ximgs is not None and (imgi_import or imge_import or seq_import or mov_import) and blib:
            img_dir = ResourceDir("images", resource_path)
            hash_dict = None
            sfv_update = False
            for ximg in ximgs:
                if ximg.attrib["source"] in {'FILE', 'GENERATED'}:
                    if ximg.attrib["origin"] == "internal":
                        if not imgi_import:
                            pass
                    else:
                        if not imge_import:
                            pass
                elif ximg.attrib["source"] == 'SEQUENCE':
                    if not seq_import:
                        pass
                elif ximg.attrib["source"] == 'MOVIE':
                    if not mov_import:
                        pass
                
                #Write image to temporary folder, and pack in Blender
                if ximg.attrib["source"] in {'FILE', 'GENERATED'} and (img_embed or (img_embed is None and ximg.attrib["origin"] == "internal")):
                    ipath = extract_image(archive, ximg.attrib["path"], str(tmp_path), path_dict, failed)
                    if ipath is None:
                        pass
                    
                    try:
                        img = bpy.data.images.load(ipath)
                    except:
                        fail(failed, "images", "import image '{}', unknown reason".format(ximg.attrib["path"]))
                    else:
                        img.source = ximg.attrib["source"]
                        try:
                            img.pack()
                        except:
                            bpy.data.images.remove(img)
                            fail(failed, "images", "pack image '{}', unknown reason".format(ximg.attrib["path"]))
                        else:
                            img.filepath = ""
                            imgs[ximg.attrib["name"]] = img
                
                else: #Write image to resource folder, and load in Blender
                    if img_merge and ximg.attrib["source"] != 'SEQUENCE': #Use existing image in resources if available
                        try:
                            comment = archive.getinfo(ximg.attrib["path"]).comment.decode("utf-8")
                        except KeyError:
                            fail(failed, "images", "import image '{}', file is missing".format(ximg.attrib["path"]))
                            pass
                        
                        com_path = path_dict[comment] if comment != "" else ""
                        com_name = path.basename(path.dirname(com_path))
                        if comment != "" and com_name != "tmp":
                            ipath = com_path
                            path_dict[ximg.attrib["path"]] = ipath
                        else:
                            #Create hash dictionary only in the first iteration
                            if hash_dict is None:
                                hash_path = path.join(img_dir.root, "list.sfv")
                                hash_dict = {}
                                if path.isfile(hash_path):
                                    sfv = re.compile(r"(.*) (.*?)$")
                                    hash_file = open(hash_path, 'r', encoding="utf-8")
                                    for line in hash_file:
                                        key = sfv.sub(r"\2", line).strip()
                                        val = sfv.sub(r"\1", line).strip()
                                        if key in hash_dict and val in hash_dict[key]:
                                            sfv_update = True
                                        else:
                                            hash_dict.setdefault(key, []).append(val)
                                    hash_file.close()
                                hash_bkp = hash_dict.copy()
                            
                            #Check if files match and set path to appropriate image
                            img_path = ximg.attrib["path"] if comment == "" else comment
                            try:
                                crc = format(archive.getinfo(img_path).CRC, 'x')
                            except KeyError:
                                fail(failed, "images", "import image '{}', file is missing".format(ximg.attrib["path"]))
                                pass
                            
                            if crc in hash_dict:
                                i = 0
                                while i < len(hash_dict[crc]):
                                    val = hash_dict[crc][i]
                                    fpath = path.join(img_dir.root, val)
                                    if path.isfile(fpath):
                                        fsize = path.getsize(fpath)
                                        zsize = archive.getinfo(img_path).file_size
                                        if fsize == zsize:
                                            ffile = open(fpath, 'rb')
                                            zfile = archive.open(img_path, 'r')
                                            if files_equal(ffile, zfile):
                                                ipath = fpath
                                                path_dict[ximg.attrib["path"]] = ipath
                                                ffile.close()
                                                zfile.close()
                                                break
                                            ffile.close()
                                            zfile.close()
                                    else:
                                        hash_dict[crc].remove(val)
                                        i -= 1
                                    i += 1
                                else:
                                    ipath = extract_image(archive, ximg.attrib["path"], str(img_dir), path_dict, failed)
                                    if ipath is None:
                                        pass
                                    
                                    hash_dict[crc].append(path.relpath(ipath, img_dir.root))
                            else:
                                ipath = extract_image(archive, ximg.attrib["path"], str(img_dir), path_dict, failed)
                                if ipath is None:
                                    pass
                                
                                hash_dict[crc] = [path.relpath(ipath, img_dir.root)]
                    else: #Use image in archive, even if duplicate
                        if ximg.attrib["source"] == 'SEQUENCE':
                            seq_dir = path.dirname(ximg.attrib["path"])
                            dir_name = ximg.attrib["path"].split("/")[-2]
                            seq_path = path.join(str(img_dir), dir_name)
                            makedirs(seq_path)
                            seq_imgs = [img for img in archive.namelist() if img.startswith(seq_dir)]
                            for img in seq_imgs:
                                i_tmp_path = extract_image(archive, img, seq_path, path_dict, failed)
                                if img == ximg.attrib["path"]:
                                    ipath = i_tmp_path
                                    if ipath is None:
                                        break
                            if ipath is None:
                                rmtree(seq_path)
                                pass
                        else:
                            ipath = extract_image(archive, ximg.attrib["path"], str(img_dir), path_dict, failed)
                            if ipath is None:
                                pass
                    
                    #load image to Blender
                    try:
                        img = bpy.data.images.load(ipath)
                    except:
                        fail(failed, "images", "import image '{}', unknown reason".format(ximg.attrib["path"]))
                    else:
                        img.source = ximg.attrib["source"]
                        imgs[ximg.attrib["name"]] = img
            
            if tmp_path:
                for item in listdir(str(tmp_path)):
                    fpath = path.join(str(tmp_path), item)
                    if path.isfile(fpath):
                        remove(fpath)
            
            #Update hash file if list has changed
            if hash_dict is not None and (hash_dict != hash_bkp or sfv_update):
                hash_path = path.join(img_dir.root, "list.sfv")
                hash_file = open(hash_path, 'w', encoding="utf-8")
                for key in hash_dict:
                    for val in hash_dict[key]:
                        hash_file.write(val + " " + key + "\n")
                hash_file.close()
        
        #Texts
        if xtxts is not None and (txti_import or txte_import):
            for xtxt in xtxts:
                if xtxt.attrib["origin"] == "internal":
                    if txti_import:
                        if "path" in xtxt.attrib:
                            if blib:
                                if txt_embed == False:
                                    import_texts("zip", "ext", xtxt, txts, failed, archive, txt_dir)
                                else:
                                    import_texts("zip", "int", xtxt, txts, failed, archive, txt_dir)
                        else:
                            if txt_embed == False:
                                import_texts("xml", "ext", xtxt, txts, failed, None, txt_dir)
                            else:
                                import_texts("xml", "int", xtxt, txts, failed, None, txt_dir)
                
                else:
                    if txte_import:
                        if "path" in xtxt.attrib:
                            if blib:
                                if txt_embed == True:
                                    import_texts("zip", "int", xtxt, txts, failed, archive, txt_dir, txt_paths)
                                else:
                                    import_texts("zip", "ext", xtxt, txts, failed, archive, txt_dir, txt_paths)
                        else:
                            if txt_embed == True:
                                import_texts("xml", "int", xtxt, txts, failed, None, txt_dir, txt_paths)
                            else:
                                import_texts("xml", "ext", xtxt, txts, failed, None, txt_dir, txt_paths)
        
        #Groups
        if xgrps is not None:
            for xgrp in xgrps:
                xnodes = xgrp.find("nodes")
                xlinks = xgrp.find("links")
                grp = bpy.data.node_groups.new(xgrp.attrib["name"], xgrp.attrib["bl_idname"])
                grps[xgrp.attrib["name"]] = grp
                if xnodes is not None:
                    build_tree(xnodes, xlinks, grp, resources, txt_embed, txt_dir, blib, script_import, archive, failed)
    
    #Import material
    xmat = xroot.find("main")
    
    if xmat is not None:
        xcycles = xmat.find("cycles_settings")
        xnodes = xmat.find("nodes")
        xlinks = xmat.find("links")
        
        mat = bpy.data.materials.new(xmat.attrib["name"])
        set_attributes(mat, xmat, failed)
        set_attributes(mat.cycles, xcycles, failed)
        mat.use_nodes = True
        mat.node_tree.nodes.clear()
        build_tree(xnodes, xlinks, mat.node_tree, resources, txt_embed, txt_dir, blib, script_import, archive, failed)
        if blib:
            archive.close()
        for f in failed:
            print("{} {} failed to be imported/assigned.".format(failed[f], f))
        return mat
    else:
        if blib:
            archive.close()
        for f in failed:
            print("{} {} failed to be imported/assigned.".format(failed[f], f))
        return grp

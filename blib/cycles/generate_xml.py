# ##### BEGIN GPL LICENSE BLOCK #####
#
# Part of the Cycles sub-package of Blib.
# Generate XML: Generates XML tree from given Blender Cycles material or node group.
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

import xml.etree.cElementTree as ET
from os import path

from .version import version, compatible
from .utils import check_asset
from ..exceptions import InvalidObject
from ..utils import fail

##### Pretty print code by Fredrik Lundh. Source: http://effbot.org/zone/element-lib.htm#prettyprint #####
def indent(elem, level=0):
    i = "\n" + level*"\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
##### End of pretty print code #####

def set_attributes(object, xelement, optimize_file):
    attrs = [attr for attr in dir(object) if not attr.startswith("__") and not attr.startswith("bl_") and type(getattr(object, attr)).__module__ == "builtins"]
    for attr in attrs:
        if not (attr == "node_tree" and hasattr(object, "type") and object.type == 'GROUP') and \
           not (attr in {"filepath", "script"} and hasattr(object, "type") and object.type == 'SCRIPT') and \
           not (attr == "text" and hasattr(object, "type") and object.type == 'FRAME') and \
           not (attr == "image" and hasattr(object, "image_user")):
            val = getattr(object, attr)
            try:
                setattr(object, attr, val)
            except AttributeError:
                pass
            else:
                if isinstance(val, str) or isinstance(val, int) or isinstance(val, float) or isinstance(val, bool) or val is None:
                    if not (optimize_file and (val == "" or val is None)):
                        xelement.set(attr, str(val))
                else:
                    try:
                        val = list(val)
                    except TypeError:
                        pass
                    else:
                        xelement.set(attr, str(val))
    return

def set_io(object, xelement, optimize_file):
    if len(object.inputs) > 0:
        xins = ET.SubElement(xelement, "inputs")
        for inp in object.inputs:
            if inp.identifier == '__extend__':
                break
            xin = ET.SubElement(xins, "input")
            set_attributes(inp, xin, optimize_file)
    
    if len(object.outputs) > 0:
        xouts = ET.SubElement(xelement, "outputs")
        for out in object.outputs:
            if out.identifier == '__extend__':
                break
            xout = ET.SubElement(xouts, "output")
            set_attributes(out, xout, optimize_file)
    return

def set_nodes(object, xelement, images, script_export, scr_paths, textnames, optimize_file):
    if len(object.nodes) > 0:
        xnodes = None
        for node in object.nodes:
            if xnodes == None:
                xnodes = ET.SubElement(xelement, "nodes")
            
            xnode = ET.SubElement(xnodes, "node")
            xnode.set("bl_idname", node.bl_idname)
            if node.parent is not None:
                xnode.set("blib_parent", node.parent.name)
            set_attributes(node, xnode, optimize_file)
            set_io(node, xnode, optimize_file)
            
            if node.type == 'GROUP':
                if node.node_tree is not None:
                    xnode.set("blib_node_tree", node.node_tree.name)
            elif node.type == 'SCRIPT':
                if node.mode == 'INTERNAL':
                    if node.script is not None and node.script.name in textnames:
                        xnode.set("blib_script", node.script.name)
                elif node.mode == 'EXTERNAL':
                    spath = bpy.path.abspath(node.filepath)
                    if spath in scr_paths:
                        xnode.set("blib_filepath", scr_paths[spath])
            elif node.type == 'FRAME':
                if node.text is not None and node.text.name in textnames:
                    xnode.set("blib_text", node.text.name)
            elif hasattr(node, "image_user"):
                if node.image in images:
                    xnode.set("blib_image", node.image.name)
                    ximageuser = ET.SubElement(xnode, "image_user")
                    set_attributes(node.image_user, ximageuser, optimize_file)
            elif hasattr(node, "mapping") and hasattr(node.mapping, "curves"):
                curvedata = [[[list(point.location), point.handle_type] for point in curve.points] for curve in node.mapping.curves]
                xcurvedata = ET.SubElement(xnode, "curve_data")
                xcurvedata.text = str(curvedata)
            elif hasattr(node, "color_ramp"):
                ramp = node.color_ramp
                rampdata = [[element.position, list(element.color)] for element in ramp.elements]
                xrampdata = ET.SubElement(xnode, "ramp_data")
                set_attributes(ramp, xrampdata, optimize_file)
                xrampdata.text = str(rampdata)
    return

def set_links(object, xelement):
    if len(object.links) > 0:
        xlinks = ET.SubElement(xelement, "links")
        for link in object.links:
            f_index = list(link.from_node.outputs).index(link.from_socket)
            t_index = list(link.to_node.inputs).index(link.to_socket)
            xlink = ET.SubElement(xlinks, "link")
            xlink.set("from_node", link.from_node.name)
            xlink.set("from_socket", str(f_index))
            xlink.set("to_node", link.to_node.name)
            xlink.set("to_socket", str(t_index))
    return

def generate_xml(object, imgi_export=True, imge_export=True, seq_export=True, mov_export=True, txti_export=True, txte_export=True,
            script_export=True, optimize_file=False, blib=False, txt_embed=False, pretty_print=False):
    """
    Generate XML representing a Cycles material or node group as per the Blib standard.
    
    Args:
        object (bpy.types.Material or bpy.types.ShaderNodeTree): The object to be exported,
            has to be Cycles object, no other renderers supported.
        imgi_export (bool): Export images that are packed in .blend file.
        imge_export (bool): Export images that are externally saved.
        seq_export (bool): Export image sequences.
        mov_export (bool): Export movies.
        txti_export (bool): Export texts that are packed in .blend file.
        txte_export (bool): Export texts that are externally saved.
        script_export (bool): Export scripts that are referenced by path in "script" node.
        optimize_file (bool): Optimize file, by not including variables qual to None or "".
        blib (bool): True only if XML is to be part of a full .blib file.
        txte_embed (bool): Embed externally saved text files into .blib file,
            should not be used if XML is to be part of a full .blib file.
        pretty_print (bool): Format XML to improve readability (increases file size),
            should only be used if XML is going to be read by a Human,
            should not be used if XML is to be part of a full .blib file.
    
    Returns:
        (xml, image_list, text_list)
        xml (bytes): byte string containing the xml.
        image_list (list[dict]): list containing the images to be exported, in format:
            list(dict{
                "image" (bpy.types.Image): Image data block,
                "destination" (str): Path to which the image should be saved in .blib file,
                "range" (tuple): Only included if image.source equals 'SEQUENCE',
                    tuple[0]: Sequence start frame.
                    tuple[1]: Sequence end frame.
                })
        text_list (list[dict]): list containing the texts to be exported, in format:
            list(dict{
                "text" (bpy.types.text): Text data block (only included for texts, and not for expernal scripts),
                "source" (str): Path to the text file (empty string when text is internal),
                "destination" (str): Path to which the text should be saved in .blib file,
                })
    
    Raises:
        blib.exeptions.InvalidObject: If the 'object' argument is not a Cycles material or node tree.
    """
    
    check_asset(object)
    
    if isinstance(object, bpy.types.Material):
        groups = [object.node_tree]
        ngroups = []
    elif isinstance(object, bpy.types.ShaderNodeTree):
        groups = [object]
        ngroups = [object]
    
    img_export = True if imgi_export or imge_export or seq_export or mov_export else False
    txt_export = True if txti_export or txte_export else False
    
    images = {}
    scripts = []
    texts = {}
    textnames = []
    failed = {}
    
    #List groups images and texts
    index = 0
    while len(groups) > index:
        for node in groups[index].nodes:
            if node.type == 'GROUP':
                ntree = node.node_tree
                if ntree is not None:
                    groups.append(ntree)
                    if ntree in ngroups:
                        ngroups.remove(ntree)
                    ngroups.append(ntree)
            elif node.type == 'SCRIPT':
                if node.mode == 'INTERNAL':
                    if txt_export and node.script is not None:
                        export = False
                        if node.script.filepath == "" or not path.isfile(bpy.path.abspath(node.script.filepath)):
                            if txti_export:
                                export = True
                                if node.script not in texts:
                                    texts[node.script] = "internal"
                        else:
                            if txte_export and (blib or txte_embed):
                                export = True
                                if node.script not in texts:
                                    texts[node.script] = "external"
                        if export and node.script.name not in textnames:
                            textnames.append(node.script.name)
                elif node.mode == 'EXTERNAL':
                    if script_export and blib and node.filepath != "":
                        spath = bpy.path.abspath(node.filepath)
                        if path.isfile(spath):
                            if spath not in scripts:
                                scripts.append(spath)
                        else:
                            fail(failed, "scripts", "export script '{}', file is missing".format(spath))
            elif node.type == 'FRAME':
                if txt_export and node.text is not None:
                    export = False
                    if node.text.filepath == "" or not path.isfile(bpy.path.abspath(node.text.filepath)):
                        if txti_export:
                            export = True
                            if node.text not in texts:
                                texts[node.text] = "internal"
                    else:
                        if txte_export and (blib or txte_embed):
                            export = True
                            if node.text not in texts:
                                texts[node.text] = "external"
                    if export and node.text.name not in textnames:
                        textnames.append(node.text.name)
            elif hasattr(node, "image_user"):
                if img_export and blib and node.image is not None:
                    if node.image.source == 'SEQUENCE':
                        if seq_export:
                            if path.isfile(bpy.path.abspath(node.image.filepath)):
                                frange = [node.image_user.frame_offset + 1, node.image_user.frame_offset + node.image_user.frame_duration]
                                if node.image in images:
                                    if images[node.image][0] > frange[0]:
                                        images[node.image][0] = frange[0]
                                    if images[node.image][1] < frange[1]:
                                        images[node.image][1] = frange[1]
                                else:
                                    images[node.image] = frange
                            else:
                                fail(failed, "images", "export sequence '{}', file is missing".format(node.image.name))
                    elif node.image.source == 'MOVIE':
                        if mov_export:
                            if path.isfile(bpy.path.abspath(node.image.filepath)):
                                frange = (node.image_user.frame_offset + 1, node.image_user.frame_offset + node.image_user.frame_duration)
                                if node.image in images:
                                    if images[node.image][0] > frange[0]:
                                        images[node.image][0] = frange[0]
                                    if images[node.image][1] < frange[1]:
                                        images[node.image][1] = frange[1]
                                else:
                                    images[node.image] = frange
                            else:
                                fail(failed, "images", "export movie '{}', file is missing".format(node.image.name))
                    elif imgi_export and node.image.packed_file is not None:
                        if node.image not in images:
                            images[node.image] = None
                    elif imge_export:
                        if path.isfile(bpy.path.abspath(node.image.filepath)):
                            if node.image not in images:
                                images[node.image] = None
                        else:
                            fail(failed, "images", "export image '{}', file is missing".format(node.image.name))
        index += 1
    
    #Copy text names and generate dictionary
    if txt_embed == True:
        txt_rel_paths = []
    elif txt_embed == False:
        txt_rel_paths = {txt: {"src": bpy.path.abspath(txt.filepath), "dst": "texts/" + txt.name} for txt in texts}
    elif txt_embed is None:
        txt_rel_paths = {txt: {"src": bpy.path.abspath(txt.filepath), "dst": "texts/" + txt.name} for txt in texts if texts[txt] == "external"}
    
    #Uniquify script names and generate dictionary
    scripts.sort(key=lambda x: bpy.path.basename(x).lower())
    scr_rel_paths = {}
    txt_rel_paths_export = txt_rel_paths.copy()
    
    index = 0
    for scr in scripts:
        for txt in txt_rel_paths_export.values():
            if txt["src"] == scr:
                scr_rel_paths[scr] = txt["dst"]
                break
        else:
            num = -1
            ok = False
            while not ok:
                if num == -1:
                    name = bpy.path.basename(scr)
                else:
                    split = path.splitext(bpy.path.basename(scr))
                    name = split[0] + "_" + str(num) + split[1]
                
                for tname in textnames:
                    if name.lower() == tname.lower():
                        num += 1
                        break
                else:
                    ok = True
                    tpath = "texts/" + name
                    txt_rel_paths_export[scr] = tpath#, "name": name
                    scr_rel_paths[scr] = tpath
    
    xroot = ET.Element("blib")
    xroot.set("type", "cycles")
    xroot.set("version", str(version))
    xroot.set("compatible", str(compatible))
    
    #Export resources
    if len(ngroups) > 0 or len(images) > 0 or len(texts) > 0:
        xres = ET.SubElement(xroot, "resources")
        
        #Images
        if len(images) > 0:
            ximgs = ET.SubElement(xres, "images")
            seqindex = 1
            for img in images:
                ximg = ET.SubElement(ximgs, "image")
                ximg.set("name", img.name)
                ximg.set("source", img.source)
                
                if img.source == 'SEQUENCE':
                    ximg.set("path", "images/sequence_" + str(seqindex) + "/" + bpy.path.basename(img.filepath))
                    seqindex += 1
                else:
                    ximg.set("path", "images/" + img.name)
                    if img.source in {'FILE', 'GENERATED'}:
                        if img.packed_file is None:
                            ximg.set("origin", "external")
                        else:
                            ximg.set("origin", "internal")
        
        #Texts
        if len(texts) > 0:
            xtxts = ET.SubElement(xres, "texts")
            for txt, val in texts.items():
                xtxt = ET.SubElement(xtxts, "text")
                xtxt.set("name", txt.name)
                xtxt.set("origin", val)
                if txt in txt_rel_paths:
                    xtxt.set("path", txt_rel_paths[txt]["dst"])
                else:
                    xtxt.text = txt.as_string()
        
        #Groups
        if len(ngroups) > 0:
            xgrps = ET.SubElement(xres, "groups")
            for grp in reversed(ngroups):
                xgrp = ET.SubElement(xgrps, "group")
                xgrp.set("bl_idname", grp.bl_idname)
                xgrp.set("name", grp.name)
                set_nodes(grp, xgrp, images, script_export, scr_rel_paths, textnames, optimize_file)
                set_links(grp, xgrp)
    
    #Export material
    if isinstance(object, bpy.types.Material):
        xmat = ET.SubElement(xroot, "main")
        xmat.set("name", object.name)
        xmat.set("diffuse_color", str(list(object.diffuse_color)))
        xmat.set("specular_color", str(list(object.specular_color)))
        xmat.set("alpha", str(object.alpha))
        xmat.set("specular_hardness", str(object.specular_hardness))
        xmat.set("pass_index", str(object.pass_index))
        
        xcycles = ET.SubElement(xmat, "cycles_settings")
        set_attributes(object.cycles, xcycles, optimize_file)
        set_nodes(object.node_tree, xmat, images, script_export, scr_rel_paths, textnames, optimize_file)
        set_links(object.node_tree, xmat)
    
    #Generate image list
    imagelist = []
    seqindex = 1
    for img, frange in images.items():
        if img.source == 'SEQUENCE':
            imagelist.append({
            "image": img,
            "destination": "images/sequence_" + str(seqindex),
            "range": frange})
            seqindex += 1
        elif img.source == 'MOVIE':
            imagelist.append({
            "image": img,
            "destination": "images/" + img.name,
            "range": frange})
        else:
            imagelist.append({"image": img, "destination": "images/" + img.name})
    
    #Generate text list
    textlist = []
    for txt, val in txt_rel_paths_export.items():
        if isinstance(txt, str):
            textlist.append({"source": txt, "destination": val})
        else:
            textlist.append({"text": txt, "source": val["src"], "destination": val["dst"]})
    
    #Pretty print
    if pretty_print:
        indent(xroot)
    
    #tree = ET.ElementTree(xroot)
    xml = b"<?xml version='1.0' encoding='utf-8'?>"
    if pretty_print:
        xml += b"\n"
    xml += ET.tostring(xroot, encoding="utf-8")
    
    for f in failed:
        print("{} {} failed to be exported.".format(failed[f], f))
    
    return xml, imagelist, textlist

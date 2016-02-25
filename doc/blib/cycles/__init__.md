#[blib](../__init__.md)[\.cycles](__init__.md)

**Source code:** [blib/cycles/\_\_init\_\_\.py](../../../blib/cycles/__init__.py)

Cycles export/import as per the Blib standard\.  

##Index
####Modules
* <code>cycles\.[**version**](version.md)</code>

####[Functions](#functions-1)
* <code>cycles\.[**bexport**](#function-cycles-bexport)</code>
* <code>cycles\.[**bimport**](#function-cycles-bimport)</code>
* <code>cycles\.[**generate\_xml**](#function-cycles-generate_xml)</code>

##Functions
* <a id="function-cycles-bexport"></a>*function* cycles\.**bexport(**<i>object, filepath, imgi\_export=True, imge\_export=True, seq\_export=True, mov\_export=True, txti\_export=True, txte\_export=True, script\_export=True, optimize\_file=False, compress=True</i>**)**  
  Export a Cycles material or node group to a \.blib file\.  

  **Arguments:**
  * <code>**object** \(*bpy\.types\.Material* or *bpy\.types\.ShaderNodeTree*\)</code>: The object to be exported,
has to be Cycles object, no other renderers supported\.
  * <code>**filepath** \(*str*\)</code>: Path to save the file\.
  * <code>**imgi\_export** \(*bool*\)</code>: Export images that are packed in \.blend file\.
  * <code>**imge\_export** \(*bool*\)</code>: Export images that are externally saved\.
  * <code>**seq\_export** \(*bool*\)</code>: Export image sequences\.
  * <code>**mov\_export** \(*bool*\)</code>: Export movies\.
  * <code>**txti\_export** \(*bool*\)</code>: Export texts that are packed in \.blend file\.
  * <code>**txte\_export** \(*bool*\)</code>: Export texts that are externally saved\.
  * <code>**script\_export** \(*bool*\)</code>: Export scripts that are referenced by path in "script" node\.
  * <code>**optimize\_file** \(*bool*\)</code>: Optimize file, by not including variables qual to None or ""\.
  * <code>**compress** \(*bool*\)</code>: Use compression on the zip container\.

  **Raises:**
  * <code>**blib\.exeptions\.InvalidObject**</code>: If the 'object' argument is not a Cycles material or node tree\.


---

* <a id="function-cycles-bimport"></a>*function* cycles\.**bimport(**<i>filepath, resource\_path, imgi\_import=True, imge\_import=True, seq\_import=True, mov\_import=True, txti\_import=True, txte\_import=True, script\_import=True, img\_embed=False, txt\_embed=None, skip\_sha1=False, img\_merge=True</i>**)**  
  Import a Cycles material or node group from a \.blib or \.xml file\.  

  **Arguments:**
  * <code>**filepath** \(*str*\)</code>: Path to \.blib or \.xml file\.
  * <code>**resource\_path** \(*str*\)</code>: Path to save external resources\.
  * <code>**imgi\_import** \(*bool*\)</code>: Import images that were packed in \.blend file\.
  * <code>**imge\_import** \(*bool*\)</code>: Import images that were externally saved\.
  * <code>**seq\_import** \(*bool*\)</code>: Import image sequences\.
  * <code>**mov\_import** \(*bool*\)</code>: Import movies\.
  * <code>**txti\_import** \(*bool*\)</code>: Import texts that were packed in \.blend file\.
  * <code>**txte\_import** \(*bool*\)</code>: Import texts that were externally saved\.
  * <code>**script\_import** \(*bool*\)</code>: Import scripts that were referenced by path in "script" node\.
  * <code>**img\_embed** \(*bool* or *None*\)</code>: Pack images\. True to pack, False to save externally,
and None to keep the setup from the exported material\.
  * <code>**txt\_embed** \(*bool* or *None*\)</code>: Pack texts\. True to pack, False to save externally,
and None to keep the setup from the exported material\.
  * <code>**skip\_sha1** \(*bool*\)</code>: Skip checksum verification\. Allows the importing of manually edited
materials, that would otherwise seem corrupted \(use with caution\)\.
  * <code>**img\_merge** \(*bool*\)</code>: If an image contained in the \.blib, is already available in the local
resources, use the existing image instead of creating a new instance\.

  **Returns:**

  <code>**bpy\.types\.Material**</code> or <code>**bpy\.types\.ShaderNodeTree**</code>  
  The produced material or node tree\.  

  **Raises:**
  * <code>**blib\.exeptions\.InvalidBlibFile**</code>: If the file is not a valid Blender Library\.
  * <code>**blib\.exeptions\.BlibTypeError**</code>: If the Blender Library is not of type "cycles"\.
  * <code>**blib\.exeptions\.BlibVersionError**</code>: If the file was created with a later, backwards incompatible version of Blib\.


---

* <a id="function-cycles-generate_xml"></a>*function* cycles\.**generate\_xml(**<i>object, imgi\_export=True, imge\_export=True, seq\_export=True, mov\_export=True, txti\_export=True, txte\_export=True, script\_export=True, optimize\_file=False, blib=False, txt\_embed=False, pretty\_print=False</i>**)**  
  Generate XML representing a Cycles material or node group as per the Blib standard\.  

  **Arguments:**
  * <code>**object** \(*bpy\.types\.Material* or *bpy\.types\.ShaderNodeTree*\)</code>: The object to be exported,
has to be Cycles object, no other renderers supported\.
  * <code>**imgi\_export** \(*bool*\)</code>: Export images that are packed in \.blend file\.
  * <code>**imge\_export** \(*bool*\)</code>: Export images that are externally saved\.
  * <code>**seq\_export** \(*bool*\)</code>: Export image sequences\.
  * <code>**mov\_export** \(*bool*\)</code>: Export movies\.
  * <code>**txti\_export** \(*bool*\)</code>: Export texts that are packed in \.blend file\.
  * <code>**txte\_export** \(*bool*\)</code>: Export texts that are externally saved\.
  * <code>**script\_export** \(*bool*\)</code>: Export scripts that are referenced by path in "script" node\.
  * <code>**optimize\_file** \(*bool*\)</code>: Optimize file, by not including variables qual to None or ""\.
  * <code>**blib** \(*bool*\)</code>: True only if XML is to be part of a full \.blib file\.
  * <code>**txte\_embed** \(*bool*\)</code>: Embed externally saved text files into \.blib file,
should not be used if XML is to be part of a full \.blib file\.
  * <code>**pretty\_print** \(*bool*\)</code>: Format XML to improve readability \(increases file size\),
should only be used if XML is going to be read by a Human,
should not be used if XML is to be part of a full \.blib file\.

  **Returns:**

  <code>\(**xml**, **image\_list**, **text\_list**\)</code>  
  <code>**xml** \(*bytes*\)</code>: byte string containing the xml\.  
  <code>**image\_list** \(*list*\[*dict*\]\)</code>: list containing the images to be exported, in format:  
  &nbsp;&nbsp;&nbsp;&nbsp;<code>*list*\(*dict*\{</code>  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>**"image"** \(*bpy\.types\.Image*\)</code>: Image data block,  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>**"destination"** \(*str*\)</code>: Path to which the image should be saved in \.blib file,  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>**"range"** \(*tuple*\)</code>: Only included if image\.source equals 'SEQUENCE',  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>*tuple*\[*0*\]</code>: Sequence start frame\.  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>*tuple*\[*1*\]</code>: Sequence end frame\.  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>\}\)</code>  
  <code>**text\_list** \(*list*\[*dict*\]\)</code>: list containing the texts to be exported, in format:  
  &nbsp;&nbsp;&nbsp;&nbsp;<code>*list*\(*dict*\{</code>  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>**"text"** \(*bpy\.types\.text*\)</code>: Text data block \(only included for texts, and not for expernal scripts\),  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>**"source"** \(*str*\)</code>: Path to the text file \(empty string when text is internal\),  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>**"destination"** \(*str*\)</code>: Path to which the text should be saved in \.blib file,  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>\}\)</code>  

  **Raises:**
  * <code>**blib\.exeptions\.InvalidObject**</code>: If the 'object' argument is not a Cycles material or node tree\.


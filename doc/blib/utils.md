#[blib](__init__.md)[\.utils](utils.md)

**Source code:** [blib/utils\.py](../../blib/utils.py)

Utility classes and functions for Blib packages\.  

####[Classes](#classes-1)
* <code>utils\.[**ResourceDir**](#class-utils-ResourceDir)</code>
* <code>utils\.[**Version**](#class-utils-Version)</code>

####[Functions](#functions-1)
* <code>utils\.[**archive\_sha1**](#function-utils-archive_sha1)</code>
* <code>utils\.[**extract**](#function-utils-extract)</code>
* <code>utils\.[**fail**](#function-utils-fail)</code>
* <code>utils\.[**files\_equal**](#function-utils-files_equal)</code>
* <code>utils\.[**gen\_crc**](#function-utils-gen_crc)</code>
* <code>utils\.[**gen\_resource\_path**](#function-utils-gen_resource_path)</code>
* <code>utils\.[**get\_path**](#function-utils-get_path)</code>
* <code>utils\.[**is\_int**](#function-utils-is_int)</code>
* <code>utils\.[**write**](#function-utils-write)</code>

##Classes
* <a id="class-utils-ResourceDir"></a>*class* utils\.**ResourceDir(**<i>name, directory=None</i>**)**  
  Keeps initialized path available, but only creates directory when the path is requested\.  
    
  Using str\(instance\) will create the directory \(if necessary\), and return the path\.  
    
  When truth checking an instance, it will be True only if the path has been requested  
  and thus the directory created, otherwise it is False\.  

  **Arguments:**
  * <code>**name** \(*str*\)</code>: Name of the resource type\.
  * <code>**directory** \(*str* or *None*\)</code>: Path to resource directory\.

  **Attributes:**
  * <code>ResourceDir\.**root** \(*read*\-*only*\[*str*\]\)</code>: Path to the root directory for the resource type\.


---

* <a id="class-utils-Version"></a>*class* utils\.**Version(**<i>version, rel\_type=None</i>**)**  
  Version control object\.  
    
  Creates multi\-part version number functionality\.  
  Using str\(instance\) returns a string containing dot separated numbers\.  

  **Arguments:**
  * <code>**version** \(*str*\)</code>: Dot separated integer string \(e\.g\. "1\.0\.2"\)
  * <code>**rel\_type** \(*str*\)</code>: Release type \(e\.g\. "beta", "stable", etc\.\)\.
Used to generate decorated string, for display purposes\.

  **Attributes:**
  * <code>Version\.**decorated** \(*str*\)</code>: Decorated string, in format "&lt;dot separated version number&gt; \(&lt;rel\_type&gt;\)" \(e\.g\. "1\.0\.2 \(stable\)"\)\.

##Functions
* <a id="function-utils-archive_sha1"></a>*function* utils\.**archive\_sha1(**<i>archive</i>**)**  
  Generate sha1 hash from crc32 hashes of all files in archive\.  

  **Arguments:**
  * <code>**archive** \(*zipfile\.ZipFile*\)</code>: The archive for which to generate the hash\.

  **Returns:**

  <code>**hashlib\.sha1**</code>: The resulting hash object\.  


---

* <a id="function-utils-extract"></a>*function* utils\.**extract(**<i>archive, item, directory</i>**)**  
  Extract item from ZIP archive, without keeping internal ZIP structure, and resolving references\.  

  **Arguments:**
  * <code>**archive** \(*zipfile\.ZipFile*\)</code>: The archive from which to extract the item\.
  * <code>**item** \(*str*\)</code>: The path to the item inside the archive\.
  * <code>**directory** \(*str*\)</code>: The path to the directory to which to extract\.

  **Returns:**

  <code>**str**</code>: Path to the extracted file\.  


---

* <a id="function-utils-fail"></a>*function* utils\.**fail(**<i>failed, f\_type, action</i>**)**  
  Increment fail counter and print fail to console\.  

  **Arguments:**
  * <code>**failed** \(*dict*\)</code>: Dictionary of fail counters\.
  * <code>**f\_type** \(*str*\)</code>: The type of fail occurred \(must be same as corresponding key in failed dict\)\.
  * <code>**action** \(*str*\)</code>: Action that failed \(e\.g\. "import", "export", "link"\.\.\.\)
  * <code>**name** \(*str*\)</code>: Name of the object on which the action failed\.
  * <code>**reason** \(*str*\)</code>: Reason for which the action failed \(e\.g\. "a &lt;some resource&gt; is missing"\)


---

* <a id="function-utils-files_equal"></a>*function* utils\.**files\_equal(**<i>file1, file2</i>**)**  
  Check if files contain same data\.  

  **Arguments:**
  * <code>**file1**, **file2** \(*file* *object*\)</code>: Files should be loaded in the same mode \(i\.e\. binary or text\),
otherwise equal files may seem different\.

  **Returns:**

  <code>**bool**</code>  


---

* <a id="function-utils-gen_crc"></a>*function* utils\.**gen\_crc(**<i>filepath</i>**)**  
  Generate crc32 hash, without loading whole file to disk\.  

  **Arguments:**
  * <code>**filepath** \(*str*\)</code>: Path to file to be hashed\.

  **Returns:**

  <code>**int**</code>: crc32 hash in decimal form\.  


---

* <a id="function-utils-gen_resource_path"></a>*function* utils\.**gen\_resource\_path(**<i></i>**)**  
  Generate path to resources relative to the module path\.  

  **Returns:**

  <code>**str**</code>: "&lt;module directory&gt;/resources"  


---

* <a id="function-utils-get_path"></a>*function* utils\.**get\_path(**<i>archive, item</i>**)**  
  Resolve reference chain\.  

  **Arguments:**
  * <code>**archive** \(*zipfile\.ZipFile*\)</code>: The archive wherein the file is located\.
  * <code>**item** \(*str*\)</code>: The path to the item inside the archive\.

  **Returns:**

  <code>**str**</code>: Path to the file within the archive\.  


---

* <a id="function-utils-is_int"></a>*function* utils\.**is\_int(**<i>string</i>**)**  
  Check if string is integer \(strict check\)\.  

  **Arguments:**
  * <code>**string** \(*str*\)</code>: string to be checked

  **Returns:**

  <code>**bool**</code>  


---

* <a id="function-utils-write"></a>*function* utils\.**write(**<i>archive, source, destination, crcs</i>**)**  
  Write data to archive, while only making a link if identical data is already in archive\.  

  **Arguments:**
  * <code>**archive** \(*zipfile\.ZipFile*\)</code>: The archive to which to write the data\.
  * <code>**source** \(*str* or *bytes*\)</code>: The path to the file to be written or the data itself\.
If source is 'str', it is interpreted as a file path\.
If source is 'bytes', it is interpreted as data to be written directly\.
  * <code>**destination** \(*str*\)</code>: The path within the archive to which the data should written\.
  * <code>**crcs** \(*dict*\)</code>: A dictionary containing crc32 hashes to all files in archive\.
Can be passed as an empty dictionary\.
Same dict should be passed every time you write to the same archive\.

  **Raises:**
  * <code>**TypeError**</code>: If the 'source' argument is not a 'str' or 'bytes' object\.


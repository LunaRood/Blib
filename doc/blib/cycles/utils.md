#[blib](../__init__.md)[\.cycles](__init__.md)[\.utils](utils.md)

**Source code:** [blib/cycles/utils\.py](../../../blib/cycles/utils.py)

Utility functions for the Cycles Blib package\.  

####[Functions](#functions-1)
* <code>utils\.[**check\_asset**](#function-utils-check_asset)</code>
* <code>utils\.[**get\_sub\_type**](#function-utils-get_sub_type)</code>

##Functions
* <a id="function-utils-check_asset"></a>*function* utils\.**check\_asset(**<i>asset, do\_raise=False</i>**)**  
  Check if asset is a Cycles material or node group,  
  and thus is exportable by the 'cycles' package\.  

  **Arguments:**
  * <code>**asset** \(*any* *type*\)</code>: Asset to be checked for validity\.
  * <code>**do\_raise** \(*bool*\)</code>: If True, an exception is raised for invalid assets,
instead of returning False\.

  **Returns:**

  <code>**bool**</code>: True if check is passed, otherwise returns False\.  
  Note that False is only ever returned if 'do\_raise' is False,  
  otherwise an exception is raised instead\.  

  **Raises:**
  * <code>**blib\.exeptions\.InvalidObject**</code>: If the check fails and 'do\_raise' is True\.


---

* <a id="function-utils-get_sub_type"></a>*function* utils\.**get\_sub\_type(**<i>archive</i>**)**  
  Get the subtype of a 'cycles' type Blib file\.  

  **Arguments:**
  * <code>**archive** \(*zipfile\.ZipFile*\)</code>: The archive to be checked\.

  **Returns:**

  <code>**str**</code> or <code>**None**</code>  
  A string containing the Blib sub\-type is returned,  
  if no valid sub\-type is found, None is returned\.  


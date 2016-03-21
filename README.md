# Blib
Blib is a Python library (and the name of the file standard it follows) for usage with Blender 3D, which enables you to export Blender assets to a standalone .blib file, and import them back for later usage.

Currently the blib package only contains a cycles subpackage, thus can only deal with Cycles material assets. But the file format was designed to accommodate any blender asset type, so it is just a matter of writing more subpackages following the same Blib standard.

* [Getting started](#getting-started)
  * [Important notes](#important-notes)
  * [Getting Blib](#getting-blib)
  * [Using Blib](#using-blib)
    * [Use Blib in your addon](#use-blib-in-your-addon)
    * [Use Blib from the Blender Python Console](#use-blib-from-the-blender-python-console)
* [Contributing](#contributing)
  * [Reporting issues](#reporting-issues)
  * [Developing Blib subpackages](#developing-blib-subpackages)
* [Asset types](#asset-types)

## Getting started
### Important notes
0. Blib is **not** a Blender addon, but a library to be used by addons. There is currently no released addon that uses this library, but I will be releasing a simple import/export one as soon as I can, and the inclusion of this library in existing addons is being discussed. So if you want to use the Blib file standard to store you Blender assets, you can do one of three things:
  * Wait for the release of an addon that supports this library.
  * Use the library from the Blender Python Console. (Explained bellow)
  * Develop your own addon around this library. (Continue reading for code examples and API reference)

0. The Blib library is currently in beta stage, and thus might contain several bugs. Furthermore, many things can change, both in the API and the file standard itself, until the consolidating 1.0.0 release. So if you use this library in its current state, be prepared for the possibility of some things breaking in future releases, and the required maintenance that comes with that.

0. Blib has been tested in Blender v2.76, and earlier versions are not supported. If you encounter issues using an earlier version of Blender, it is recommended that you update to the latest version. If the issues persist, please refer to [reporting issues](#reporting-issues) for more information on how to file an issue report.

### Getting Blib
You can download the latest version of Blib as a .zip of .tar.gz archive at the [releases page](../../releases).

It is important to download from the [releases page](../../releases), and **not** directly from the repository in its current state, as it reflects a development state, and is not required to be in a working condition.

### Using Blib
Here I will cover both how to use Blib within your addon, and how to use it as a standalone command line utility.

#### Use Blib in your addon
To use the Blib library in your addon, you can just extract the downloaded archive (.zip or .tar.gz), and copy the "blib" directory into your addon's root directory.

The "blib" directory is a Python package that may contain multiple subpackages (one for each supported asset type). You may optionally delete any **subpackage** that your addon is not going to use, to make its distribution more compact. However, be warned that all **modules** within the root of the blib package, are critical for its operation, and thus will almost certainly generate errors if deleted.

To use the import and export functions of a Blib subpackage, your import should look something like:
```python
from blib.<asset_type> import bimport, bexport
```
Where &lt;asset_type&gt; is the Blib codename for the asset type you want to manipulate. You can find the supported asset types and their Blib codenames in the [asset types](#asset-types) list.

Now here is a simple code example using the cycles subpackage to export and import a Cycles material using all the default options:
```python
import bpy
from blib.cycles import bimport, bexport

#Exporting
#This example shows how to export the active material
mat = bpy.context.active_object.active_material # Get the active material
path = "path_to_output_directory/filename.blib"
bexport(mat, path) # Only the required arguments are passed, so the default options will be used

#Importing
path = "path_to_file_directory/filename.blib"
bimport(path) # Only the required argument is passed, so the default options will be used
```

It is recommended however, that you familiarize yourself with all the options these functions provide, by reading the API references for [bimport](doc/blib/cycles/__init__.md#function-cycles-bimport) and [bexport](doc/blib/cycles/__init__.md#function-cycles-bexport)

#### Use Blib from the Blender Python Console
The first thing you have to do, is make to the blib package available to Blender. To do that you just extract the downloaded archive (.zip or .tar.gz), and copy the "blib" directory into your Blender modules directory:

|OS|Directory|
|:---|:---|
|Linux|$HOME/.config/blender/&lt;your version&gt;/scripts/modules|
|OSX|/Users/$USER/Library/Application Support/Blender/&lt;your version&gt;/scripts/modules|
|Windows|C:\\Documents and Settings\\$USERNAME\\AppData\\Roaming\\Blender Foundation\\Blender\\&lt;your&nbsp;version&gt;\\scripts\\modules|

If that directory doesn't exist, you can just create it.

Now that you have Blib properly installed, you can load Blender, and open a "Python Console" area.
The first command you'll have to type in, is to load the desired Blib subpackage:
```python
from blib.<asset_type> import bimport, bexport
```
Where &lt;asset_type&gt; is the Blib codename for the asset type you want to manipulate. You can find the supported asset types and their Blib codenames in the [asset types](#asset-types) list.

Now, here is some example usage of the cycles subpackage, used to export Cycles material:

You can use one of the following commands to export a material with all the default options (to learn all the available options, refer to the API reference for [bexport](doc/blib/cycles/__init__.md#function-cycles-bexport)):
```python
#Export active material
bexport(C.active_object.active_material, "path_to_output_directory/filename.blib")

#Export arbitrary material
bexport(D.materials["name of the material"], "path_to_output_directory/filename.blib")
```

And this command to import a material with all the default options (to learn all the available options, refer to the API reference for [bimport](doc/blib/cycles/__init__.md#function-cycles-bimport)):

```python
#Import material
bimport("path_to_file_directory/filename.blib")
```

## Contributing
You can contribute to Blib in several ways:
* Testing Blib, and [report any issues you find](#reporting-issues).
* [Developing addons using Blib](#use-blib-in-your-addon), to help bring it to the users and popularize the standard.
* [Develop additional subpackages](#developing-blib-subpackages), to enable Blib to deal with more asset types. (Not yet possible)

### Reporting issues
If you encounter a bug or issue with Blib, before reporting it make sure you are using the latest released version of blib (you can check the latest version on the [releases page](../../releases)), and Blender version 2.76 or later, as no previous versions are officially supported.

Once you verified all of the above, you can head to the [issues page](../../issues), and click the "New issue" button.  
Start by giving it a short and descriptive title. Then you write your report in the following format, replacing the fields with the appropriate info:
```
* **Platform:** Linux/OSX/Windows
* **Blender version:** 2.76
* **Steps to reproduce:**
  0. Do this
  0. Do that
  0. Do this other thing
* **Expected behavior:** This is what should actually happen.

If you feel like the title and the above info are not enough to describe the issue,
here you can write a more thorough description of the issue.
```
Note that the list of steps to reproduce, should be numbered with zeroes ("0"), and will automatically be replaced by the correct numbers.

Now the only thing that is left, is to add the "bug" label to the issue.

You can also request a feature, by doing the same as above, but just describing the feature instead of writing the shown info, and by swapping the "bug" label for a "feature" label.

### Developing Blib subpackages
It is not currently possible for you to develop Blib subpackages, as despite of the API being fully documented, the file standard is not.

## Asset types
|Blib codename|Asset type description|
|:---|:---|
|cycles|Any object of type 'bpy.types.Material' or 'bpy.types.ShaderNodeTree', that is specifically a Cycles material or node group.|

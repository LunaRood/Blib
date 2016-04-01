# [blib](__init__.md)[\.exceptions](exceptions.md)

**Source code:** [blib/exceptions\.py](../../blib/exceptions.py)

Generic Blib exceptions, independent of specific sub\-packages\.  

#### [Exceptions](#exceptions-1)
* <code>exceptions\.[**BlibException**](#exception-exceptions-BlibException)</code>
* <code>exceptions\.[**BlibTypeError**](#exception-exceptions-BlibTypeError)</code>
* <code>exceptions\.[**BlibVersionError**](#exception-exceptions-BlibVersionError)</code>
* <code>exceptions\.[**InvalidBlibFile**](#exception-exceptions-InvalidBlibFile)</code>
* <code>exceptions\.[**InvalidObject**](#exception-exceptions-InvalidObject)</code>

## Exceptions
* <a id="exception-exceptions-BlibException"></a>*exception* exceptions\.**BlibException**  
    Blib base exception, should never be raised\.  
    Should be the base class for any blib exception, even sub\-package specific exceptions\.  
    Only use to sub\-class exceptions, or to catch any Blib exception\.  


---

* <a id="exception-exceptions-BlibTypeError"></a>*exception* exceptions\.**BlibTypeError**  
    Raised when the \.blib file is not of the correct type for the operation\.  


---

* <a id="exception-exceptions-BlibVersionError"></a>*exception* exceptions\.**BlibVersionError**  
    Raised when the passed file was created with a later, backwards incompatible version of Blib\.  


---

* <a id="exception-exceptions-InvalidBlibFile"></a>*exception* exceptions\.**InvalidBlibFile**  
    Raised when the passed file is not a Blib file, or is broken\.  


---

* <a id="exception-exceptions-InvalidObject"></a>*exception* exceptions\.**InvalidObject**  
    Raised when the passed object, is not compatible with that exporter\.  


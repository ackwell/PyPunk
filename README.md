PyPunk2
=======

A python game library (heavily) inspired by the ActionScript3 library FlashPunk by ChevyRay.

Known Issues
------------

* Users with ATI GPUs may notice odd display behaviour occuring. This is an issue with the
  card itself, and there is absoultely nothing I can do about it. Primarily occurs when
  non-bitmap graphics are used.

Dependencies
------------

* Python 2 or 3 (Tested in py3.3)
  * This library is primarily targeted at Python 3.x, although should also support recent
    versions of Python 2. If you notice any bugs in the library while running Python 2, please
    tag the bug report with the `python2-support` tag.
* [pySFML](http://www.python-sfml.org/) 1.3.0

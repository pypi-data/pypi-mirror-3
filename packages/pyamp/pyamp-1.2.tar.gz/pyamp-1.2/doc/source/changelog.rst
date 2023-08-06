================================================================================
Changelog
================================================================================

The following page describes all of the changes that were made for specific
versions of pyamp.

----------------------------------------
Release 1.2
----------------------------------------

1. Added acceptedValues, and caseSensitive properties to the Option base class.
   This allows the user to specify a list of values which the must be. The
   option parser class will throw an Exception in the event that an Option
   has a value that was not specified in the list of accepted values. This
   also allows the values to be case sensitive, or case insensitive.

2. Added the ability to apply a Prefix chain to the LogData class. This allows
   a single Prefix chain to be applied to all the Loggers created for an
   entire system.

----------------------------------------
Release 1.1
----------------------------------------

1. Added this page to the documentation to list the changes made to each version.
2. Created the 'html' module which provides the ability to more easily manage
   the content of HTML pages.
3. Created more utility modules: directories, functions, inspection, html,
   and lists.
4. Added a module for automatically generating RST files for a Python project.
5. Using the rstGeneration module to generate the documentation for pyamp.
6. Fixed small bug in rstGeneration script.
7. Updated setup.py so distributions can be created and uploaded to the Python
   Package Index.
8. Bumped versions in documentation and setup.py accordingly.

----------------------------------------
Release 1.0
----------------------------------------

Initial release of pyamp.

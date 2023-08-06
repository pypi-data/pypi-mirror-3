================================================================================
Changelog
================================================================================

The following page describes all of the changes that were made for specific
versions of pysiriproxy.

----------------------------------------
Release 0.0.5
----------------------------------------

1. Using StringIO to send a string containing plist data to CFPropertyList
   instead of writing a file and deleting the file afterward.

----------------------------------------
Release 0.0.4
----------------------------------------

1. Using the biplist module to convert plist objects created by
   CFPropertyList into binary plists. The previous method was to call the
   external plutil Perl script. This was reported as causing significant
   delays (0.5 to 1.5 seconds) while running pysiriproxy on an iPhone. This
   change solves that issue by doing the conversion in Python rather than
   using the Perl script.

2. Updated setup.py script to allow distributions to be created and uploaded
   to the Python Package Index.

3. Updated the documentation to include installation instructions for biplist,
   and for using setuptools to install pysiriproxy.

----------------------------------------
Release 0.0.3
----------------------------------------

1. The connection to the Guzzoni web server is now tied to the iPhone
   connection. The Guzzoni connection is only established once the iPhone
   connection is finished, and both are closed when the iPhone connection
   is lost. This resolves an issue where the server was no longer usable
   after a long period of inactivity -- the Guzzoni connection was closed
   and not being re-established.
2. Added the ability to create map locations and send them to the iPhone
   user so that they are displayed in a list of locations.
3. Added the ability to send directions between two locations to the
   iPhone user which are displayed in the map. The directions can be:
   walking, driving, or public transportation directions.
4. Created a new plugin to demonstrate how to create locations and
   directions.

----------------------------------------
Release 0.0.2
----------------------------------------

1. Documentation updated to fix small mistakes in installation instructions on
   Ubuntu 11.10, and 12.04.
2. The siriproxy script has been made executable to persist through the SVN
   checkout.
3. Added documentation on the changes made to each version of pysiriproxy.
4. Fixed issue with sequential requests not working. The new requests were
   blocked by the previously matched plugin causing the Siri button to continuously
   spin. Now the context is reset on a request completed message (which should
   be sent at the completion of all Plugins). This keeps new requests from being
   blocked, and allows Siri to properly respond to a series of questions.

----------------------------------------
Release 0.0.1
----------------------------------------

Initial release of pysiriproxy.

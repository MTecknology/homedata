.. _refactor-diagrow:

Delete Diagnostics Rows
=======================

A quick hack of a script used to clean up a database when multiple
applications have finished processing the data.

This was refactored because it was originally running under a terminated
user's screen session and had no error handling logic. It was written so
that it could run comfortably as a daemon.

Original Version
----------------

.. literalinclude:: old.py

Biggest Issues
--------------

- Must be run interactively (daemonized via screen)
- Requires restart to change any settings
- Logging used, but required script edits to activate
- Required constant restart to continue operating

New Version
-----------

.. literalinclude:: new.py

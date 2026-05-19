.. _refactor-backuplist:

Backup List
===========

This is a quick snippet that demonstrates how it's easy to over-complicate
what should be simple solutions.

Original Version
----------------

.. literalinclude:: old.jinja

Biggest Issues
--------------

- Creates a variable then loops through a list, adding to list for each iteration
- Includes an if that is not needed
- New version just adds them to the list/tuple being defined

New Version
-----------

.. literalinclude:: new.jinja

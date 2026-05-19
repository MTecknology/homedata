.. _refactor-runtests:

Run Tests
=========

This script is used in a Jenkins/Kitchen test suite.

Original Version
----------------

.. literalinclude:: old.sh
   :language: sh

Biggest Issues
--------------

- Spaghetti logic (option parsing from start to end)
- Options provide limited value (mostly for modifying personal directory)
- Haphazard option parsing and heavy use of environment variables
- Lots of bugs that require pre-/post-execution tasks

New Version
-----------

- Uses functions to organize logic
- Fully backward-compatible
- Supports short and long arguments (long was considered a hard requirement)
- Lots more built-in documentation
- Exposes helpful options
- Lots more logging

.. literalinclude:: new.sh
   :language: sh

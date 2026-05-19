.. _refactor-keyscan:

SSH-Keyscan
===========

Check out the :ref:`archives ssh-keyscan project <ssh-keyscan>` to see final version.

Original Version
----------------

.. literalinclude:: old_1.pl
   :language: perl

Biggest Issues
--------------

- Extremely slow
- Does not support threading
- Unreliable detection (both false-positives and false-negatives)
- Many bugs that cause script to crash
- Requires a lot of hand-holding to execute and monitor
- Often crashes without an exit status

New Version
-----------

This is an interim version; :ref:`the final version became a new project <ssh-keyscan>`.

.. literalinclude:: new.py

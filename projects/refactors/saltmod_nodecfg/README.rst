.. _refactor-nodecfg:

Salt Module: NodeCFG
====================

This module worked similar to pillar.get() except that it was designed to
operate on a shared pillar dictionary. It was rewritten because the old
version had many bugs and broke the standard assumptions. This temporary
module was eventually deprecated in favor of a system that doesn't use
shared dictionaries.

Original Version
----------------

This is not the original version. There were too many bugs that needed urgent
fixing and then a repository reset lost the original.

.. literalinclude:: old.py

Biggest Issues
--------------

- ``.get()`` behavior is extremely non-standard (was ``.get(hostname, key, default, missing_ok)``)
- Confusing ``.get()`` usage created hidden bugs across entire repository

  + Often swapped default value and lookup hostname
  + Lots of changing default in every config

- Required every single pillar value (secret) to be exposed to every single host
- Lots of code that didn't do what was described
- Imported delimeter but never used it

New Version
-----------

.. literalinclude:: new.py

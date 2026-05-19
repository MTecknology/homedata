.. _refactor-parselog:

Parse Ansible Log
=================

This is a quick helper script to parse ansible logs for analysis.

Original Version
----------------

.. literalinclude:: old.py

Biggest Issues
--------------

- Most of script buried underneath ``if __name__ == "__main__":``
- No comments
- Lots of looping over same set of data
- Spaghetti logic
- Insufficient validation checks

New Version
-----------

.. literalinclude:: new.py

.. _refactor-pipeauth:

Jabberd2 Pipe-Auth
==================

This script is used by the jabberd2-c2s process to verify user credentials
against an custom internal application.

This was refactored because the old version was not able to handle the full
load from production, could not cache credentials, and was very slow. It was
rewritten to run more like a daemon than a script. Caching was originally
built into the single-threaded process but later transitioned to redis which
added support for shared cache between redundant systems and removed cache
rebuild time during application startup.

Original Version
----------------

.. literalinclude:: old.py

Biggest Issues
--------------

- Extremely slow
- Grabs a cache key but does not use it
- Actual production deployment used ``AUTH_ALL=1`` to deal with high load
- Huge sections of try/except logic

New Version
-----------

- Adds internal cache
- Final version swapped internal variables with redis key/values

  + Cache did not require rebuild across service restarts
  + Allowed a shared cached between all servers

- Adds signal handling in order to change log level without restart
- Lots of attention to useful log messages

.. literalinclude:: interim.py

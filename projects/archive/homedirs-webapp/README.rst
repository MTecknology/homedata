.. _project-homedirs:

HomeDirs
========

This was written in order to automate time-consuming processes.

It makes use of "ajax"-style requests, redis-rq, and the bottle framework.


Front-End Controller
--------------------

.. literalinclude:: app.py

Module: Login
-------------

.. literalinclude:: modules/login.py

Module: File Move
-----------------

Relocate files from terminated users into manager directory.

.. literalinclude:: modules/filemove.py

Module: File Restore
--------------------

Queue file for restoration from tape and eventually send files and notice to user.

.. literalinclude:: modules/filerestore.py

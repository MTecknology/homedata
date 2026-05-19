Old Refactors
=============

.. toctree::
   :hidden:
   :maxdepth: 3

   backup_list/README
   delete_diagnostics_rows/README
   parse_ansible_log/README
   pipe-auth/README
   run_tests/README
   saltmod_nodecfg/README
   ssh-keyscan/README

A subset of projects where my primary goal was to radical improvement, often
because a proof-of-concept failed to scale.

   ==========================  =============
   Project                     Short Summary
   ==========================  =============
   :ref:`refactor-backuplist`  Demonstration of over-complicated code/logic
   :ref:`refactor-diagrow`     Slow and buggy script that needed to run inside of screen
   :ref:`refactor-parselog`    Quick helper script to analyze ansible logs
   :ref:`refactor-pipeauth`    Authenticate users and devices against django backend
   :ref:`refactor-runtests`    Wrapper script that launched kitchen/jenkins tests
   :ref:`refactor-nodecfg`     Module that completely broke security in salt-pillar
   :ref:`refactor-keyscan`     Used to scan for insecure/passwordless SSH keys
   ==========================  =============

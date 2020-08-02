SSH Key Scanner - Includes
==========================

This directory contains non-python extras used by the the key scanner utility.

is_ssh_ok
---------

This script is primarily an end-user/self-service utility used to check SSH keys
for compliance with Juniper Networks Policies. Additional information is available
in the file header; usage is available by running the script with --ssh.

In order to ensure the automated key scans don't remove unexpected directories,
this script is also used as a dependency of ``keyscan`` to verify whether or not
a key is policy compliant.

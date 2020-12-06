SSH Key Scanner
===============

This set of scripts is used to scan user directories for unencrypted SSH keys
and securely upload results to sharepoint.

Source Code
-----------

Source code for the scanner is available at `gitlab/foo/ssh-keyscan`_.

To grab a copy of this source::

    git clone https://git.domain.tld/ssh-keyscan.git /opt/ssh-keyscan

.. _gitlab/foo/ssh-keyscan: https://git.domain.tld/ssh-keyscan

Scanning Nodes
--------------

Currently: svl-scanner, bng-scanner, qnc-scanner, wfd-scanner

Scanning is done using the ``keyscan.py`` script.

If the input file (default: ``./targets``) does not exist, then the script will
attempt to make one using the autofs file (default: ``/etc/auto.homes``).
The input file is expected to be a list of usernames. Scanning will be performed
against "``<base>`` + ``<user>`` + (optionally) ``/.ssh``".

If the ``--delete`` argument is passed, then ``scandir`` will attempt to delete
any unencrypted ssh keys that are found.

More options and their descriptions can be seen with the ``--help`` option.

Scan results will be stored in ``<output_dir>/<user>``.

AutoFS File
+++++++++++

An ``autofs`` file is required in order to automatically mount user's home
directories when scanning for unprotected ssh keys. Each geographic location
has it's own file. This file should be located at ``/etc/auto.homes``.

In order for autofs to read this file, the line ``/scanhomes /etc/auto.homes``
must appear in ``/etc/auto.master``.

Updated files can be downloaded from the `ConfigMgmt`_ repository.

.. note:: These files are undergo daily arbitrary changes; always grab a fresh copy.

AutoFS Set Up::

    apt install autofs
    OR yum install -y autofs nfs-utils perl-File-MMagic perl-Parallel-ForkManager
    mkdir /scanhomes
    echo "/scanhomes    /etc/auto.homes" >> /etc/auto.master
    wget <ConfigMgmt>/all/<geo>/auto.homes -O /etc/auto.homes
    service autofs restart

.. _ConfigMgmt: https://git.domain.tld/ConfigMgmt/tree/master/all

Run Time
++++++++

It can take an extremely long time for scans to run. Therefore, it's best to
begin scans from inside a screen or tmux session.

Example Usage::

    screen  # re-attach with -r
    pushd /opt/keyscan/
    ./keyscan.py --ssh  # scan for keys in /<base>/<user>/.ssh

    # new scan
    rm <output_dir>/*
    ./keyscan.py

Known Issues
------------

The autofs files provided are not clean, meaning cross-geo entries exist. This
causes problems with parallel (multi-threaded) scans because every user from
an inaccessible NFS host causes a delay that blocks other automounts, which then
causes others to hang.

As a band-aid, when ``keyscan.py`` builds a ``targets`` list from ``auto.homes``,
it will attempt to mount all NFS mount paths and exclude all users that have a
directory on a path that cannot be mounted. Checking each mount path is a
sequential and time-consuming process but largely eliminates the named problems.

If a ``targets`` list is built manually, then running ``keyscan.py`` with the
``--single-thread`` option can prevent problems by avoiding multiple mounts waiting
for an eventual timeout.

Setting ``timeout: 30`` in ``autofs.conf`` reduces overall waits for a timeout.

Configuration File
------------------

In order for scanners to upload results to sharepoint, credentials need to be
configured. This configuration is expected to be at ``$config_dir/upload.yml``;
the default ``$config_dir`` is ``/etc/keyscan``.

Sample upload.yml (with sample values)::

    sp_url: https://sharepoint.domain.tld
    sp_team: /teams/SecMon
    sp_site: /engineering/monitoring
    sp_folder: "/monitoring/Public Information/SSH Scan Results"
    username: scanner@domain.tld
    password: SuperSecret

.. note:: Keep $config_dir secure (750) ;; Be careful with leading/trailing slashes

Finding Correct Values
++++++++++++++++++++++

The ``sp_*`` configuration values are made up from the following template::

    https://<sharepoint_addr>/<team>/<site>/<folder>

Example::

    https://sp.domain.tld/teams/SecMon/tools/monit/Reports/SSH Scan Results

    sharepoint_addr: sp.domain.tld
    team: /teams/SecMon
    site: /tools/monit
    folder: /Reports/SSH Scan Results

Either Firefox + Tamper Data or Chrome + packet capture can be used to get a bettecr
idea of what the correct attributes should be. Further information can be obtained
from the Sharepoint `Digest Reference`_ and `Upload Reference`_.

.. _Digest Reference: https://docs.microsoft.com/en-us/sharepoint/dev/sp-add-ins/complete-basic-operations-using-sharepoint-rest-endpoints
.. _Upload Reference: https://docs.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-folders-and-files-with-rest

.. _hacking-development:

Development
============

Welcome to all developers daring to brave these sources!

Prerequisites
-------------

Developing GitLight should be easy, and maybe even fun. However, any potential
contributors should be warned that GitLight requires all contributions maintain
a very high level of quality.

The first thing any contributor *MUST* do is read the following documents.

- :ref:`hacking-code_standards`
- `Code of Conduct`_
- `Contribution Rules`_

.. _Code of Conduct: https://github.com/gitlight/gitlight/blob/develop/CODE_OF_CONDUCT.md
.. _Contribution Rules: https://github.com/gitlight/gitlight/blob/develop/.github/CONTRIBUTING.md

For developers looking to make contributions, it mostly boils down to:

- Once merged, your code is is not your code.
- *ALL* commits *MUST* be signed with a GPG key.
- Be nice.

Vagrant Dev
-----------

Using vagrant provides a convenient method to bootstrap a new development
environment. It ensures a clean environment where tests, documentation,
coverage, etc. can easily be checked prior to upload.

Only Codacy checks cannot be run locally. Developers are free to create a Codacy
account and configure reviews of their fork, but doing so is beyond the scope of
this documentation.

Virtualbox
++++++++++

Virtualbox is a simple virtualization tool that works across different platforms.
Linux users can [download a package or add a repository]
(https://www.virtualbox.org/wiki/Linux_Downloads) to let their package manager
keep virtualbox up to date. Virtualbox also supports [Windows, OSX, and Solaris]
(https://www.virtualbox.org/wiki/Downloads).

In some scenarios (usually Linux), the vbox extension pack needs to be added.

- Visit the [virtualbox download](https://www.virtualbox.org/wiki/Downloads) page
- Under ``VirtualBox Extension Pack``, download via ``All supported platforms``
- Open virtualbox, as root
- File > Preferences > Extensions
- Click ``+`` and select the downloaded file
- Click Install, READ the license, choose your fate
- Close this virtualbox instance (since it's root)

Vagrant Quickstart
++++++++++++++++++

.. note:: This vagrant configuration supports ``vagrant-cachier`` for apt caching.

Once virtualbox is installed and configured, vagrant can deploy an instance with:

.. code:: bash

    cd /path/to/gitlight
    vagrant up

During deployment, the bootstrap will:

- Updates system packages
- Installs package dependencies
- Create a py3 virtualenv for ~vagrant
- Configure .bashrc for ~vagrant
- Create a git user
- Install and configure gitolite3
- Create a 'demo' plugins/config in ``/etc/gitolite/``
- Symlink config dir to ~vagrant (convenience)
- Mount the source repository as ``/home/vagrant/dev``
- Install uWSGI
- Configure uWSGI to serve both Agent and App
- Configure Nginx to serve "all the things" (see config)

These components are easy to toggle/modify and represent a realistic deployment.
To aid development, the uWSGI configurations used here are tuned for debugging.
uWSGI will watch for file changes and reload with file changes. This should
eliminate the need for ``make run``, but that functionality hasn't been removed
and is supported by the installed Nginx configuration.

When the bootstrap processes completes, it can be logged in to with ``vagrant ssh``.

The image is configured to forward three ports:

-   ``tcp/5055`` - gitlight application (nginx -> make run)
-   ``tcp/5070`` - gitlight application (nginx -> uwsgi)
-   ``tcp/5071`` - gitlight documentation (nginx -> make docs)

These can be reached by directing your browser to ``http://127.0.0.1:<PORT>/``.

Documentation is static. Once built by ``make docs`` from the ``~/dev/`` directory,
documentation will become available to the browser.

.. code:: bash

    # build documentation
    make docs

    # run gitlight
    sudo make run

While sudo is not required to run gitlight, elevated privileges are required in
order for gitlight to access gitolite3 repositories.

After development is complete, or if something broke and can't be explained,
destroying the box is easily accomplished with:

.. code:: bash

    vagrant destroy

Making Changes
--------------

.. warning:: *ALL* commits *MUST* be signed with a GPG key.

Making changes is best done in a personal fork with a dedicated branch.

If you forked gitlight on github, then the process would look similar to this:

.. code:: bash

    git clone git@github.com/USERNAME/gitlight
    cd gitlight

    git remote add upstream https://github.com/gitlight/gitlight
    git fetch --tags upstream

    git branch -b MY-CHANGES upstream/develop

Changes can now be made on the ``MY-CHANGES`` branch.

When submitting a Pull Request, make sure to check the diff. If the wrong branch
was selected, the changeset can be much larger than expected.

Note: Only bug fixes will be backported to supported release branches. New
features must be submitted to ``develop``.

Testing Verification
--------------------

The following tests are available to run locally and will be run as part of the
CI pipeline:

.. code:: bash

    # Run all integration tests
    make test

    # Build documentation
    make docs

    # Python lint checker
    make lint

    # Simple spell checker
    make spell

    # Check test coverage (no display for non-issue lines)
    make cov-text

    # or...
    make lint spell coverage docs; cat _build/*.txt

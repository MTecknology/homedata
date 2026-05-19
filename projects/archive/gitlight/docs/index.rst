.. _index:

.. toctree::
   :hidden:
   :includehidden:
   :maxdepth: 3

   walkthrough
   hacking
   ref/index

.. warning::

    This documentation (and project) are currently under heavy initial development.

Welcome to GitLight
===================

GitLight is a simple/lightweight collaboration tool built on top of Gitolite3.

Vision
------

GitLight has three primary design goals...

**Security**

A heavy emphasis is placed on secure design. Rather than depending on tens
(or hundreds) of additional (often, poorly maintained/unreviewed) modules,
GitLight focuses on using well-tested/reviewed modules with active development
teams.

Additionaly, GitLight is intended to run read-only to Gitolite3. Rather than
manipulating git repositories, users are presented with the commands they need
to run in order to perform actions.

GitLight uses a client-daemon model which limits the reach of many potential
vulnerabilities. It's read-only nature provides another layer of security.

**Stability**

By sticking with well-tested libraries and keeping the number of dependencies
low, GitLight is able to avoid making changes just to keep up with changes in
those dependencies.

**Simplicity**

GitLight is not meant to be a kitchen sink solution. It is meant to bring the
most useful features from other platforms into a small, stable, and secure
application that is easy to deploy and easy to develop.

**Modularity**

GitLight is designed to be flexible and modular. It aims to be easy to extend
with modules that are easy to write.

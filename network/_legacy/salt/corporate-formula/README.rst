Demo: Corporate-Formula
=======================

Unlike other saltstack-formula repositories, this project aims to showcase what
corporate-style formulas can look like.

The design presented here is less flexible than other 3rd-party formulas, such
as the formulas available on https://github.com/saltstack-formulas. Instead,
this design focuses on being simple with just enough salt magic to provide the
flexibility the environment needs. A well-written formula model can be extremely
beneficial to corporations because it (should):

* Reduce the need for all staff to understand Salt
* Reduce the size and number of states written
* Reduce technical debt
* Reduce chance of introducing errors
* Make contributions much easier to review, audit, test, deploy

This is not a magic-bullet solution. It is a simplified version of a solution
that has worked well for many corporations. It's important to have a complete
understanding of the environment to come up with the most optimal structure.

The formulas and pillar data here were written with the following hosts in mind:

* prd-aptproxy1-1.corp.domain.tld - caching apt proxy
* prd-aptproxy1-2.corp.domain.tld - caching apt proxy
* prd-pubweb2-54.corp.domain.tld  - run nginx and uwsgi (apps: saneapp, subapp)
* prd-pubweb2-59.corp.domain.tld  - run nginx and uwsgi (apps: saneapp, subapp)
* prd-syslog-1.corp.domain.tld    - collect system logs

The custom module, provided by ``_modules/mycorp_utils.py``, is used to parse the
minion ID based on a standardized naming convention. Parsing in this way provides
the benefit of ensuring systems are named correctly.

The regular expresion in the module matches this pattern::

    <service_level>-<application>[cluster_id]-<host_id>.<class>.<domain>.<tld>

In this corporate formula demo:

* All systems send syslog data to the syslog server
* The ``ferm`` formula is required by other formulas
* Formulas are underneath the ``pkgs/`` directory
* Formulas can be broken out into separate repositories; see ``pkgs/_template/``

This is a simplified version of states/pillar taken from:

https://github.com/MTecknology/salt-demo

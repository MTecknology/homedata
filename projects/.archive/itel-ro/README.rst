Ingress Intelligence Scraper
============================

This script is used to scrape comms data from the Ingress Intel API.

Process
-------

The basic process this script goes through is:

1. Read /etc/scrape_intel.conf (selects a random user from the list)
#. Open the intel site without session data
#. Follow the Google SSO process and prime Intel requests (valid session)
#. Begin requesting intel data from best possible timestamp
#. Optionally write data to file
#. Optionally send data to logstash
#. Periodically perform requests to mimic a typical conversation

Configuration File
------------------

The configuration file must contain, at a minimum, a single user.

Location: /etc/scrape_plexts.yml || ./scrape_plexts.yml

Sample File w/ defaults::

    # Performs random requests to mimic a typical client
    random_requests: True

    # Writes/reads last timestamp to/from <timestamp_file>
    save_state: True

    # File to write the timestamp to
    timestamp_file: '/tmp/intel_epoc'

    # Standard request headers
    std_headers:
        User-Agent: 'Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.7.1'
        Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        Accept-Language: 'en-US,en;q=0.5'
        Accept-Encoding: 'gzip, deflate'
        DNT: 1

    # Area to scan
    area:
      min:
        lon: -180000000
        lat: -90000000
      max:
        lon: 180000000
        lat: 90000000

    # A user will be randomly selected from this list and used for the whole session
    users:
        <username_1>: '<password_1>'
        <username_2>: '<password_2>'
        <username_3>: '<password_3>'

    # If set, a json output file will be created / appended to
    #output_file: /tmp/plexts.json

    # If set, data will be push to this logstash server
    #output_logstash: ls.domain.tld

Minimum required configuration::

    output_file: /tmp/plexts.json
    users:
        <user>: <pass>

Requisites
----------

* python-bs4
* python-requests
* python-yaml
* /etc/scrape_plexts.yml || ./scrape_plexts.yml

Notes
-----

* An attempt to read/write /tmp/intel_epoch is made to retain state between executions
* The typical client waits 90 seconds between plext requests
* If 50 plexts were returned, a new request is made immediately
* If only a few plexts were returned, the client will wait 2 minutes

Locations
---------

Sioux Falls Area::

    area:
      min:
        lon: -100640259
        lat: 42931493
      max:
        lon: -93367310
        lat: 44944585

Los Angeles Area::

    area:
      min:
        lon: -118801346
        lat: 33635774
      max:
        lon: -117043533
        lat: 34402944

Global::

    area:
      min:
        lon: 180000000
        lat: 90000000
      max:
        lon: -180000000
        lat: -90000000

Authors
-------

* Michael Lustfield <michael@profarius.com>

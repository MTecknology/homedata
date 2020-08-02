{# Skeleton bits required to query netbox. #}

salt-cloud:
  pkg.installed:
    - pkgs:
      - python3-ipy
      - python3-urllib3
      - python3-netaddr

/etc/salt/minion.d/cloud.conf:
  file.managed:
    - source: salt://etc/salt/master.d/cloud.conf
    - template: jinja
    - mode: 640
    - require:
      - pkg: salt-minion
    - listen_in:
      - service: salt-minion

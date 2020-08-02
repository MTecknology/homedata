salt-cloud:
  pkg.installed:
    - pkgs:
      - salt-cloud
      - python3-ipy
      - python3-urllib3
      - python3-netaddr

{% for d in ['conf', 'deploy', 'providers', 'profiles'] %}
/etc/salt/cloud.{{ d }}.d:
  file.recurse:
    - source: salt://etc/salt/cloud.{{ d }}.d
    - template: jinja
    - file_mode: 640
    - dir_mode: 700
    - clean: True
    - require:
      - pkg: salt-cloud
{% endfor %}

{% for m in ['master', 'minion'] %}
/etc/salt/{{ m }}.d/cloud.conf:
  file.managed:
    - source: salt://etc/salt/master.d/cloud.conf
    - template: jinja
    - mode: 640
    - require:
      - pkg: salt-{{ m }}
    - listen_in:
      - service: salt-{{ m }}
{% endfor %}

/etc/salt/cloud.map:
  file.managed:
    - source: salt://etc/salt/cloud.map
    - template: jinja
    - mode: 640
    - require:
      - pkg: salt-cloud

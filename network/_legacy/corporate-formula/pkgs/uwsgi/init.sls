{% from 'pkgs/uwsgi/defaults.sls' import conf with context -%}
include:
  - users.www-data
  # Note: This is only needed if 'pkgs.ferm' is not already part of the state run.
  - pkgs.ferm

uwsgi:
  pkg.installed:
    - pkgs:
      - uwsgi
      {% for dep in conf['deps'] %}
      - {{ dep }}
      {% endfor %}
    - require_in:
      # NOTE: This introduces a cross-formula dependency
      - file: /etc/ferm/ferm.conf
  service.running:
    - enable: True
    - require:
      - user: www-data
      - pkg: uwsgi

{% for site in conf['apps'] %}
/etc/uwsgi/apps-enabled/{{ site }}.ini:
  file.managed:
    - source: salt://etc/uwsgi/apps-enabled/{{ site }}.ini
    - follow_symlinks: False
    - user: root
    - clean: True
    - require:
      - pkg: uwsgi
    - listen_in:
      - service: uwsgi
{% endfor %}

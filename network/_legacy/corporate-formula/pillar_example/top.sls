{% set app_group = salt.mycorp_utils.app_group_from_id(grains['id']) %}
{% if not app_group %}{% set app_group = 'invalid' %}{% endif %}

'base':
  '*':
    - base

  'prd-aptproxy*':
    - ignore_missing: True
    - pkgs.apt-cacher-ng.{{ app_group }}

  'prd-syslog*':
    - pkgs.syslog.server

  'prd-pubweb*':
    - ignore_missing: True
    - nginx.{{ app_group }}
    - uwsgi.{{ app_group }}

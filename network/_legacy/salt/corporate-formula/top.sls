{% set app_group = salt.mycorp_utils.app_group_from_id(grains['id']) %}

base:

  'kernel:Linux':
    - match: grain
    - pkgs.ferm
    - pkgs.syslog
    - pkgs.repo

  # Cluster-based includes
  {% if app_group %}
  '{{ grains['id'] }}':
    - _includes._nil
    {% filter indent(width=4, indentfirst=0) -%}
    {% include '_includes/' ~ app_group ignore missing with context %}
    {% endfilter %}
  {% endif %}

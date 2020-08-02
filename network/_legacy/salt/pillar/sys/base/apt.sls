debian_apt:
{% if salt.match.grain('lsb_distrib_release:10*') %}
  release: buster
  version: 10
  salt_ver: 10
  salt_rel: buster
  server: apt.lustfield.net
  salt_server: apt.lustfield.net
{% elif salt.match.grain('lsb_distrib_release:9*') %}
  release: stretch
  version: 9
  salt_ver: 9
  salt_rel: stretch
  server: apt.lustfield.net
  salt_server: apt.lustfield.net
{% endif %}
  # Disabled, no current need.
  mtrepo: False

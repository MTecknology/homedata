{% if salt.match.grains('osfullname:Debian') %}
include:
  - pkgs.repo.deb

{% elif salt.match.grains('osfullname:Redhat') %}
include:
  - pkgs.repo.rhel

{% endif %}

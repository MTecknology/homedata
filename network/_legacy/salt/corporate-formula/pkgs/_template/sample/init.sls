{% from 'pkgs/SAMPLE/defaults.sls' import conf with context -%}

# If an application installation might influence firewall rules built by ferm,
# then ``pkgs.ferm`` should be included and the state installing the package
# should use ``require_in`` on the ferm configuration file
#include:
#  - pkgs.ferm

pkg_name:
  pkg.installed: []
  # - require_in:
  #   - file: /etc/ferm/ferm.conf
  file.managed:
    - name: /etc/pkg/config
    - source: salt://pkgs/SAMPLE/templates/config
  service.running:
    - enable: True
    - onchanges:
      - file: pkg_name

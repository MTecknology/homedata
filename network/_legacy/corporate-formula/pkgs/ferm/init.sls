ferm:
  pkg.installed: []
  service.running:
    - watch:
      - file: /etc/ferm/ferm.conf
    - require:
      - pkg: ferm
    - sig: init
    - order: last
  file.managed:
    - name: /etc/ferm/ferm.conf
    - source: salt://pkgs/ferm/templates/ferm.conf
    - template: jinja
    - order: last

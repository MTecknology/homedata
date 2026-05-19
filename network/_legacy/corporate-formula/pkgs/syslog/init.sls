{% from 'pkgs/syslog/defaults.sls' import conf with context -%}
rsyslog:
  pkg.installed:
    - require:
      - file: /etc/rsyslog.d/log.conf
  service.running:
    - require:
      - pkg: rsyslog
    - watch:
      - file: /etc/rsyslog.d/log.conf

/etc/rsyslog.d/log.conf:
  file.managed:
    - source: salt://pkgs/syslog/templates/{{ conf['logconf'] }}

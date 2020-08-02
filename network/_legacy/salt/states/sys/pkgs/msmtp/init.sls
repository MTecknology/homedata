ssmtp:
  pkg.purged: []

postfix:
  pkg.purged: []

msmtp:
  pkg.installed:
    - name: msmtp-mta

/etc/msmtprc:
  file.managed:
    - source: salt://etc/msmtp/msmtprc
    - template: jinja
    - require:
      - pkg: msmtp

/etc/aliases:
  file.managed:
    - source: salt://etc/aliases

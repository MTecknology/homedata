{% from 'sys/pkgs/plex-server/defaults.sls' import conf with context -%}
##
# TV Show Scanner/Downloader: Sonarr
# Movie Scanner/Downloader:   Radarr
##

##
# Sonarr:
#   http://plex.lustfield.net:8989/
##
sonarr:
  pkgrepo.managed:
    - name: 'deb http://apt.sonarr.tv/ master main'
    - file: /etc/apt/sources.list.d/sonarr.list
    - key_url: salt://etc/apt/keys/D9B78493.pub
    - dist: master
  pkg.installed:
    - name: nzbdrone
    - require:
      - pkgrepo: sonarr
  file.managed:
    - name: /etc/systemd/system/sonarr.service
    - source: salt://etc/systemd/system/sonarr.service
  cmd.wait:
    - name: systemctl daemon-reload
    - watch:
      - file: sonarr
  service.running:
    - name: sonarr
    - enable: True
    - watch:
      - pkg: sonarr
      - cmd: sonarr
    - require:
      - file: sonarr
      - pkg: sonarr
      - user: plex-user

##
# Radarr:
#   http://plex.lustfield.net:7878/
##
radarr:
  archive.extracted:
    - name: /opt/
    - source: "https://github.com/Radarr/Radarr/releases/download/v{{ conf['radarr-version'] }}/Radarr.develop.{{ conf['radarr-version'] }}.linux.tar.gz"
    - source_hash: {{ conf['radarr-cksum'] }}
    - user: plex
    - group: plex
  file.managed:
    - name: /etc/systemd/system/radarr.service
    - source: salt://etc/systemd/system/radarr.service
  cmd.wait:
    - name: systemctl daemon-reload
    - watch:
      - file: radarr
  service.running:
    - enable: True
    - watch:
      - archive: radarr
    - require:
      - file: radarr
      - archive: radarr
      - user: plex-user

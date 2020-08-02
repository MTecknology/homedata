{% from 'sys/pkgs/plex-server/defaults.sls' import conf with context -%}
##
# Torrent Indexer API: Jackett
# Torrent Downloader:  qBittorrent
##

##
# Sonarr/Radarr Indexer:
#   Name: Jackett
#   Indexer: http://plex.lustfield.net:9117/api/v2.0/indexers/torrentday/results/torznab/
#   Categories: 5030,5040
##

##
# Jackett:
#   http://plex.lustfield.net:9117/
##
jackett:
  archive.extracted:
    - name: /opt/
    - source: "https://github.com/Jackett/Jackett/releases/download/v{{ conf['jackett-version'] }}/Jackett.Binaries.LinuxAMDx64.tar.gz"
    - source_hash: {{ conf['jackett-cksum'] }}
    - user: root
    - group: root
  file.managed:
    - name: /etc/systemd/system/jackett.service
    - source: salt://etc/systemd/system/jackett.service
  cmd.wait:
    - name: systemctl daemon-reload
    - watch:
      - file: jackett
  service.running:
    - enable: True
    - watch:
      - archive: jackett
    - require:
      - file: jackett
      - archive: jackett
      - user: plex-user

##
# qBittorrent:
#   http://plex.lustfield.net:8088/
##
qbittorrent:
  pkg.installed:
    - name: qbittorrent-nox
  file.managed:
    - name: /etc/systemd/system/qbittorrent.service
    - source: salt://etc/systemd/system/qbittorrent.service
  cmd.wait:
    - name: systemctl daemon-reload
    - watch:
      - file: qbittorrent
  service.running:
    - enable: True
    - watch:
      - pkg: qbittorrent
    - require:
      - file: qbittorrent
      - pkg: qbittorrent
      - user: plex-user

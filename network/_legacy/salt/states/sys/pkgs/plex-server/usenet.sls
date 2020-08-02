##
# Usenet Downloader: SABnzbd
#
# Sonarr/Radarr Indexer:
#   Name: NzbGeek
#   Indexer: https://api.nzbgeek.info/
#   Categories: 5030,5040
#
# UsenetServer: https://accounts.usenetserver.com/
##

##
# Usenet Downloader:
#   http://plex.lustfield.net:8080/
##
sabnzbdplus:
  pkg.installed:
    - pkgs:
      - sabnzbdplus
      - unrar-free
    - require:
      - pkg: avahi-daemon
  service.running:
    - enable: True
    - require:
      - pkg: sabnzbdplus
      - service: plex
      - file: /home/plex
      - user: plex-user
    - watch:
      - file: sabnzbdplus
  file.managed:
    - name: /etc/default/sabnzbdplus
    - source: salt://etc/default/sabnzbdplus

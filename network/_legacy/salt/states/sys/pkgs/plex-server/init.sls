include:
  - sys.users.plex
  - sys.pkgs.git-client
  - sys.pkgs.plex-server.mono
  - sys.pkgs.plex-server.usenet
  - sys.pkgs.plex-server.torrent
  - sys.pkgs.plex-server.managers

plex:
  pkgrepo.managed:
    - humanname: "Plex Repo"
    - name: "deb https://downloads.plex.tv/repo/deb public main"
    - dist: "public"
    - file: /etc/apt/sources.list.d/plex.list
    - key_url: salt://etc/apt/keys/3ADCA79D.pub
  pkg.installed:
    - name: plexmediaserver
    - refresh: True
    - require:
      - pkgrepo: plex
      - user: plex-user
  service.running:
    - name: plexmediaserver
    - require:
      - pkg: plex

/home/plex:
  file.directory:
    - user: plex
    - group: plex
    - require:
      - user: plex

/srv/plex:
  file.directory:
    - user: plex
    - group: plex
    - dir_mode: "750"
    - require:
      - user: plex

avahi-daemon:
  pkg.installed:
    - name: avahi-daemon
  file.comment:
    - name: /etc/avahi/avahi-daemon.conf
    - regex: '^rlimit-nproc'

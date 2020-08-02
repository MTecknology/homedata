mono:
  pkgrepo.managed:
    - humanname: "Mono Xamarin"
    - name: "deb http://download.mono-project.com/repo/debian buster main"
    - dist: "buster"
    - file: /etc/apt/sources.list.d/mono-xamarin.list
    - key_url: salt://etc/apt/keys/D3D831EF.pub
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

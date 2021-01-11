Media Server
============

Disk
----

- /srv/media: xfs, 4 TB
- /srv/media/cache, xfs, 1 TB
- /srv/media/config, ext4, 10 GB 
- /var/lib/docker, xfs,  10G

Notes
-----

- First startup of each app requires initial configuration.
- Read linuxserver documentation for configuration instructions.

Docker Stuff
------------

I hate docker, but half of these applications are a horrific mess and docker
is a great way to stuff it all away and not think about it. It also makes
updates much more reliable (for the same reason).

/srv/media/update::

    #!/bin/sh
    docker-compose pull
    docker-compose up --force-recreate --build -d
    docker image prune -f


/srv/media/docker-compose.yml::

    version: '2.1'
    services:

      qbittorrent:
        image: ghcr.io/linuxserver/qbittorrent
        container_name: qbittorrent
        hostname: qbittorrent
        network_mode: media_network
        ports:
          - '8080:8080'
          - '6881:6881'
          - '6881:6881/udp'
        environment:
          - PUID=2001
          - PGID=2001
          - VERSION=docker
          - TZ=America/Central
        volumes:
          - /srv/media/config/qbittorrent:/config
          - /srv/media/cache/qbittorrent:/downloads
          - /srv/media/cache/sonarr:/downloads/sonarr
          - /srv/media/cache/radarr:/downloads/radarr
        restart: unless-stopped

      sabnzbd:
        image: ghcr.io/linuxserver/sabnzbd
        container_name: sabnzbd
        hostname: sabnzbd
        network_mode: media_network
        ports:
          - '8088:8080'
        environment:
          - PUID=2001
          - PGID=2001
          - VERSION=docker
          - TZ=America/Central
        volumes:
          - /srv/media/config/sabnzbd:/config
          - /srv/media/cache/sabnzbd:/downloads
          - /srv/media/cache/sonarr:/downloads/sonarr
          - /srv/media/cache/radarr:/downloads/radarr

      jackett:
        image: ghcr.io/linuxserver/jackett
        container_name: jackett
        hostname: jackett
        network_mode: media_network
        ports:
          - '9117:9117'
        environment:
          - PUID=2001
          - PGID=2001
          - VERSION=docker
          - TZ=America/Central
        volumes:
          - /srv/media/config/jackett:/config
          - /srv/media/cache/jackett:/downloads

      radarr:
        image: ghcr.io/linuxserver/radarr
        container_name: radarr
        hostname: radarr
        network_mode: media_network
        ports:
          - '7878:7878'
        environment:
          - PUID=2001
          - PGID=2001
          - VERSION=docker
          - TZ=America/Central
        volumes:
          - /srv/media/config/radarr:/config
          - /srv/media/cache/radarr:/downloads/radarr
          - /srv/media/data/movies:/movies

      sonarr:
        image: ghcr.io/linuxserver/sonarr
        container_name: sonarr
        hostname: sonarr
        network_mode: media_network
        ports:
          - '8989:8989'
        environment:
          - PUID=2001
          - PGID=2001
          - VERSION=docker
          - TZ=America/Central
        volumes:
          - /srv/media/config/sonarr:/config
          - /srv/media/cache/sonarr:/downloads/sonarr
          - /srv/media/data/shows:/tv

      plex:
        image: ghcr.io/linuxserver/plex
        container_name: plex
        hostname: plex
        network_mode: media_network
        ports:
          - '32400:32400'
          - '32400:32400/udp'
          - '32469:32469'
          - '32469:32469/udp'
          - '5353:5353/udp'
          - '1900:1900/udp'
        environment:
          - PUID=2001
          - PGID=2001
          - VERSION=docker
          - TZ=America/Central
        volumes:
          - /srv/media/config/plex:/config
          - /srv/media/data/movies:/movies
          - /srv/media/data/shows:/tv
          - /srv/media/data/music:/music
        devices:
          - '/dev/dri:/dev/dri'
        restart: unless-stopped

Backup Stuff
------------

/srv/media/.restic_backup::

    #!/bin/bash
    export B2_ACCOUNT_ID='foo'
    export B2_ACCOUNT_KEY='bar'

    restic -r b2:mteck-media backup \
        --limit-upload 5120 \
        --password-file /root/.restic_pw \
        --files-from /srv/media/.restic_include \
        --exclude-file /srv/media/.restic_exclude \
        --cleanup-cache \
        --quiet

/srv/media/.restic_include::

    /srv/media/.restic*
    /srv/media/docker-compose.yml
    /srv/media/update
    /srv/media/config/**
    /srv/media/data/**

/srv/media/.restic_exclude::

    .cache/**
    logs/**
    logs*
    updater.tx*
    log.tx*
    MediaCover/**
    *.db
    *.pid
    rss/**
    GeoDB/**
    Library/*
    Log*
    Logs/**
    lost+found/**
    Metadata/**
    Cache/**
    Crash Reports/**
    Diagnostics/**
    Media/**

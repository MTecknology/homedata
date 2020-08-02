/etc/resolv.conf:
  file.managed:
    - contents: |
        nameserver 10.41.50.18
        nameserver 10.41.50.23
        nameserver 9.9.9.9
        search lustfield.net

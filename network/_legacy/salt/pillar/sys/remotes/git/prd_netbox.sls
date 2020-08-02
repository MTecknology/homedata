git_remotes:
  - remote: https://github.com/digitalocean/netbox.git
    local: /srv/webapps/netbox
    #identity: /root/.ssh/id_pubweb_rsa
    revision: v2.6.11
    req_in:
      - "service: nginx"
      - "service: uwsgi"

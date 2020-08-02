git_remotes:
  - remote: git@git.lustfield.net:pubweb/api-mlustfield
    local: /srv/webapps/api-mlustfield
    identity: /root/.ssh/id_pubweb_rsa
    req_in:
      - 'service: nginx'
      - 'service: uwsgi'

  - remote: git@git.lustfield.net:pubweb/mlustfield-site
    local: /srv/webapps/mlustfield-site
    revision: master
    identity: /root/.ssh/id_pubweb_rsa
    depth: 5
    force_clone: True
    force_reset: True
    req:
      - 'file: ssh_pubweb_priv'
    req_in:
      - 'cmd: mlustfield_buildsite'
      - 'service: uwsgi'

  - remote: git@git.lustfield.net:pubweb/mlustfield-search
    local: /srv/webapps/mlustfield-search
    revision: master
    identity: /root/.ssh/id_pubweb_rsa
    depth: 5
    force_clone: True
    force_reset: True
    req:
      - 'file: ssh_pubweb_priv'
      - 'pip: pip-sphinxalchemy'
      - 'pip: pip-bottle-sqlalchemy'
    req_in:
      - 'service: uwsgi'

  - remote: git@git.lustfield.net:pubweb/contact-form
    local: /srv/webapps/contact-form
    revision: master
    identity: /root/.ssh/id_pubweb_rsa
    depth: 5
    force_clone: True
    force_reset: False
    req:
      - 'file: ssh_pubweb_priv'
    req_in:
      - 'service: uwsgi'

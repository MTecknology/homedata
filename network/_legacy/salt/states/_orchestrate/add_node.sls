git_pillar:
  runner.git_pillar.update

refresh_pillar:
  local.saltutil.refresh_pillar:
    - tgt: 'prd\-(salt,lb,ns).*\.core\.lustfield\.net'
    - tgt_type: 'pcre'
    - require:
      - runner: git_pillar

# Refresh cloud.map on file system ;; Reading from pillar would be better
build_cloudmap:
  local.state.sls:
    - tgt: 'prd-salt*.core.lustfield.net'
    - arg:
      - 'sys.pkgs.salt-cloud'
      - 'sys.pkgs.salt-master'
      - 'sys.pkgs.salt'
    - require:
      - local: refresh_pillar

deploy_node:
  local.cloud.profile:
    - tgt: 'prd-salt-01.core.lustfield.net'
    - arg:
      - {{ TODO }}
    - require:
      - local: build_cloudmap

node_highstate:
  local.state.highstate:
    - tgt: {{ TODO }}
    - require:
      - local: deploy_node

update_infra:
  local.state.highstate:
    - tgt: 'prd\-(lb,ns,snap).*\.core\.lustfield\.net'
    - tgt_type: 'pcre'
    - require:
      - local: node_highstate


##
# Execute cloud.map_run ;; Using the salt-cloud runner would be better
#create_and_destroy:
#  salt.function:
#    - name: cloud.map_run
#    - tgt: 'prd-salt-01.core.lustfield.net'
#    - kwarg:
#        path: /etc/salt/cloud.map
#    - require:
#      - salt: build_cloudmap
##

git_pillar:
  runner.git_pillar.update

refresh_pillar:
  local.saltutil.refresh_pillar:
    - tgt: 'prd\-(salt,lb,ns).*\.core\.lustfield\.net'
    - tgt_type: 'pcre'
    - require:
      - runner: git_pillar

build_cloudmap:
  local.state.sls:
    - tgt: 'prd-salt*.core.lustfield.net'
    - arg:
      - 'sys.pkgs.salt-cloud'
      - 'sys.pkgs.salt-master'
      - 'sys.pkgs.salt'
    - require:
      - local: refresh_pillar

update_infra:
  local.state.highstate:
    - tgt: 'prd\-(lb,ns).*\.core\.lustfield\.net'
    - tgt_type: 'pcre'
    - require:
      - local: git_pillar

destroy_node:
  local.cloud.destroy:
    - tgt: 'prd-salt-01.core.lustfield.net'
    - arg:
      - {{ TODO }}
    - require:
      - local: update_infra

purge_backups:
  local.cmd.run:
    - tgt: 'prd-snap-*.core.lustfield.net'
    - arg:
      - 'userdel -rf {{ TODO }}'
    - require:
      - local: destroy_node

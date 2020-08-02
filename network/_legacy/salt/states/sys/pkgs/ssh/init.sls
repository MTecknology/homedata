{% from 'sys/pkgs/ssh/defaults.sls' import conf with context -%}

ssh:
  pkg.installed:
    - name: openssh-server
  service.running:
    - require:
      - pkg: ssh
    - watch:
      - file: /etc/ssh/sshd_config

/etc/ssh/sshd_config:
  file.managed:
    - source: salt://etc/ssh/sshd_config
    - template: jinja

{% for key, data in conf['keys'].items() %}
ssh_{{ key }}_priv:
  file.managed:
    - name: {{ data['path'] }}
    - user: {{ data['user'] }}
    - group: {{ data['user'] }}
    - mode: 600
    - contents_pillar: ssh:keys:{{ key }}:privkey

ssh_{{ key }}_pub:
  file.managed:
    - name: {{ data['path'] }}.pub
    - user: {{ data['user'] }}
    - group: {{ data['user'] }}
    - mode: 644
    - contents_pillar: ssh:keys:{{ key }}:pubkey
{% endfor %}

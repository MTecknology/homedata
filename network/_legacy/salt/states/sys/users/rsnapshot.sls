# Note: MD5 is used to limit backup users to 32 characters.
#       Server names are at /home/<node>/.server_name
bkupnode:
  group.present

{% for server, keys in salt.mine.get('*', 'ssh.user_keys').items() %}
{% set user = server|md5 -%}
{{ server }}:
  user.present:
    - name: {{ user }}
    - createhome: True
    - optional_groups:
      - ssh-user
      - bkupnode
    - require:
      - group: ssh-user
      - group: bkupnode
  ssh_auth.present:
    - user: {{ user }}
    - names: [ {{ keys['root']['id_rsa.pub'] }} ]
    - options:
      - 'command="/usr/bin/rdiff-backup --server"'
      - 'no-port-forwarding'
      - 'no-x11-forwarding'
      - 'no-agent-forwarding'
    - fingerprint_hash_type: md5

# Ensures the user directory is never readable by others
/home/{{ user }}:
  file.directory:
    - user: {{ user }}
    - group: {{ user }}
    - mode: '0700'
    - require:
      - user: {{ server }}

/home/{{ user }}/.server_name:
  file.managed:
    - contents: {{ server }}
{% endfor %}

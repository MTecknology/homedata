{% from 'pkgs/nginx/defaults.sls' import conf with context -%}

# Include dependencies
# Note: This is only needed if 'pkgs.ferm' is not already part of the state run.
include:
  - pkgs.ferm

nginx:
  pkg.installed:
    - refresh: True
    - require_in:
      # NOTE: This introduces a cross-formula dependency
      - file: /etc/ferm/ferm.conf
  service.running:
    - reload: True
    - listen:
      - file: /etc/nginx/sites-enabled/default
      - file: /etc/nginx/conf.d/no-tokens.conf
      - file: /etc/nginx/conf.d/ssl-settings.conf

/etc/nginx/ssl:
  file.directory:
    - dir_mode: 700
    - require:
      - pkg: nginx

/srv/webapps:
  file.directory

{% for k in conf['webcerts'].keys() %}
/etc/nginx/ssl/{{ k }}:
  file.managed:
    - contents_pillar: nginx:webcerts:{{ k }}
    - require:
      - file: /etc/nginx/ssl
{% endfor %}

/etc/nginx/conf.d/no-tokens.conf:
  file.managed:
    - contents: |
        server_tokens off;
    - require:
      - pkg: nginx

/etc/nginx/conf.d/ssl-settings.conf:
  file.managed:
    - contents: |
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        ssl_ciphers 'kEECDH+CHACHA kEECDH+AESGCM HIGH+kEECDH AESGCM 3DES !SRP !PSK !DSS !MD5 !LOW !MEDIUM !aNULL !eNULL !DH !kECDH';
        ssl_stapling on;
        ssl_stapling_verify on;
        #ssl_dhparam ssl/dhparam.pem;
        ssl_session_tickets off;
        ssl_protocols TLSv1.2;
    - require:
      - pkg: nginx

/etc/nginx/sites-enabled/default:
  file.absent:
    - require:
      - pkg: nginx

{% for site in conf['sites'] %}
/etc/nginx/conf.d/{{ site }}.conf:
  file.managed:
    - source: salt://pkgs/nginx/configs/{{ site }}.conf
    - follow_symlinks: False
    - require:
      - pkg: nginx
    - watch_in:
      - service: nginx
{% endfor %}

{% from 'sys/pkgs/sphinxsearch/defaults.sls' import conf with context -%}
sphinxsearch:
  pkg.installed:
    - name: sphinxsearch
  service.running:
    - enable: True
    - require:
      - pkg: sphinxsearch
      - file: /etc/default/sphinxsearch

sphinxsearch-indexer:
  cmd.wait:
    - name: /usr/bin/indexer --all --noprogress --quiet --rotate
    - watch:
      - file: /etc/sphinxsearch/sphinx.conf

## files

/etc/default/sphinxsearch:
  file.managed:
    - contents: 'START=yes'

{% if conf['sphinxconf'] %}
/etc/sphinxsearch/sphinx.conf:
  file.managed:
    - source: salt://etc/sphinxsearch/sphinx.conf%%{{ conf['sphinxconf'] }}
    - require:
      - pkg: sphinxsearch
    - require_in:
      - service: sphinxsearch
      - cmd: sphinxsearch-indexer
    - watch_in:
      - service: sphinxsearch
{% endif %}

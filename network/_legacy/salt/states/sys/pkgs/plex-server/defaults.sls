{% set conf = salt.grains.filter_by(
  {
    'default': {
      'jackett-version': 'NOVERSION',
      'radarr-version': 'NOVERSION',
    },
  },
  grain = 'os_family',
  merge = salt.pillar.get('plex-server')
) %}

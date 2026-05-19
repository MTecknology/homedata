{% set conf = salt.grains.filter_by(
  {
    'default': {
      'logconf': 'client',
    },
  },
  grain = 'os_family',
  merge = salt.pillar.get('syslog')
) %}

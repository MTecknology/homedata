{% set conf = salt.grains.filter_by(
  {
    'default': {
      'allow_root': 'no',
      'keys': {},
    },
  },
  grain = 'os_family',
  merge = salt.pillar.get('ssh')
) %}

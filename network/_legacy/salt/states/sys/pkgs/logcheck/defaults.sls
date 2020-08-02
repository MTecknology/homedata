{% set conf = salt.grains.filter_by(
  {
    'default': {
      'extra_ignores': [],
    },
  },
  grain = 'os_family',
  merge = salt.pillar.get('logcheck')
) %}

{% set conf = salt.grains.filter_by(
  {
    'default': {
      'foo': {}
    },
    # Delete if not needed; can also match on a different grain
    'Debian': {
    },
    'Redhat': {
    }
  },
  grain = 'os_family',
  merge = salt.pillar.get('SAMPLE')
) %}

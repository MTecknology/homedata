{% set conf = salt.grains.filter_by(
  {
    'default': {
      'netbox_api_url': None,
      'netbox_api_token': None,
    },
  },
  grain = 'os_family',
  merge = salt.pillar.get('salt-cloud')
) %}

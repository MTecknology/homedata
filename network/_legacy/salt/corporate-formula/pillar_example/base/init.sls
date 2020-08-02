include:
  - base.repo.{{ salt.grains.get('osfullname', '') | lower }}

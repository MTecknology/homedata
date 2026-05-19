uwsgi:
  apps:
    - saneapp
    - subapp
  deps:
    - python-bottle
    - uwsgi-plugin-python
    - python-redis
    - python-pelican

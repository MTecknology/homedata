zones:
  - prd-ipmi-01.core.lustfield.net. IN A 10.41.7.81
  - prd-ipmi-02.core.lustfield.net. IN A 10.41.7.82
  # Alias for prd-glweb.core.gitlight.io; issues using LB addr
  #- ci.gitlight.io. IN A 10.41.51.19
  # Alias for prd-glweb-01.core.gitlight.io
  - ci.gitlight.io. IN A 10.41.51.20
blacklist:
  - 'top.'
  - 'pw.'
  - 'trade.'

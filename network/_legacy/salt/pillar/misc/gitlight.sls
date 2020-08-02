#!jinja|yaml|gpg
{% if salt.match.glob('prd-glweb*.gitlight.io') -%}
drone:
  backends:
    glci:
      - 10.41.51.24
    glgit:
      - 10.41.51.22

{% elif salt.match.glob('prd-glci*.gitlight.io') -%}
drone:
  version: 0.8
  config_server:
    DRONE_ADMIN: MTecknology
    DRONE_OPEN: 'false'
    DRONE_ORGS: gitlight
    DRONE_GITHUB: 'true'
    DRONE_HOST: https://ci.gitlight.io
    DRONE_RUNNER_CAPACITY: 8
    DRONE_LOGS_DEBUG: 'false'
    DRONE_GITHUB_CLIENT: |
        -----BEGIN PGP MESSAGE-----

        hQIMA9RfKrevXiv4AQ//SyhhMC/Ovm+OVnE1wvp+ZTxL7fOoxjBQwWfFsm8IWFzk
        Qds22sCnfb+zj27VmwOWRAmzjJV9m3D9z4jdoLxzjfuTdxHHwdp06jnQwtJCuRNs
        pxpxujoaUo6p45ywk/WMOQNVel4XgSjD7TTKQ9LP6fckZztdkvfmCKG8vX5CQDXu
        h+s0XcBKpwSLgxwtccrhGV4OdFqADahGqLO28eQnUc0a2H7GEiFdU6ggTD9ey72x
        TwELy6vAE4SqIspuL4DtEyQRsYoiCvY7968Ki3DnbygiRs2Cs1G5NrBiDto4ztrT
        vmg6cRqwMbj1y7mWP+lK3FynTtaseOTynfNvl+YCpiI=
        =w+zO
        -----END PGP MESSAGE-----
    DRONE_GITHUB_SECRET: |
        -----BEGIN PGP MESSAGE-----

        hQIMA9RfKrevXiv4AQ//UQlUiIj9iPHrfjdobGhitJarZ68gU4SN5hihgjYFmnJk
        p+dQU43JPjXKtCqUFBpfoNVP8eLlpvQwZ0va+TME29mWJez3qzkbcT/gusAlOQ3k
        O1EqqUyxyXR/H4vUAA7XdXVLVDJnKsMO4lS9r1G8B7wE+B2HhdAmzeie9CSbHaGz
        SSGiNjY9q+ruLVQqf8Q2rT3tw559zE/YZ7TeqKjSBrXcugmp2RiX3eM7QN7j0EQd
        B/7A/X/XsDeoIdg+1ZHJMm2O6n2OMj1rsv+yPMB4ePs7mgzKmYSCe7+KweXik43S
        YwEBcql+rNXZY5k3BNKX6YxpAtU+X4cbekllgWBRRpEY3YjFU/JP60U9F5VPaC5Q
        bqlE983W3X27FS8QtvyoR+CmVTrrwAdea7qHk06jzkQu/XKJD+sWjRejRcHx6iMb
        Ppknkw==
        =2AUz
        -----END PGP MESSAGE-----
    DRONE_SECRET: |
        -----BEGIN PGP MESSAGE-----

        hQIMA9RfKrevXiv4AQ/+N6Dgh9yKzWtcFfB5h0ry6UYjig4a15ftAqRWXPZ6oNaW
        wvW4cfdw5mBMjG4CraGiO4QpJi7RMOqfltlgJMObQbgMPl2tHwvT6Z+eENU42dvZ
        JsgIuyoXG5XC5bZjRNmWy5hwk8+GCye8k6rD7Jr/2LYjK+8CIBY/mmq/QUKOeJpy
        aKBb3IYbFoKs4/bkS5RzIQNMlM8kL2CCy3zrtaLruk7zNRyFKyGLQzQ7MhtNq7TS
        dwHNoQP6ZcYJQwSiLUmTtsZzTBKfDZ4Kh4tkmYBFBn6dHqRVc5trzLVC+El4Ifxc
        iT0b6PwhvQfWE1FOHLgj8X3CdPWhA7tjpvALjNJaEpplLAisIRCaQTtk4bPnBSvE
        0NZ7Oh5cjL3OVAKyRChbgT5mKWYB35Vb
        =Q+xi
        -----END PGP MESSAGE-----
  config_agent:
    DRONE_HOST: https://ci.gitlight.io
    DRONE_SERVER: drone-server:9000
    DRONE_LOGS_DEBUG: 'false'
    DRONE_SECRET: |
        -----BEGIN PGP MESSAGE-----

        hQIMA9RfKrevXiv4AQ/+N6Dgh9yKzWtcFfB5h0ry6UYjig4a15ftAqRWXPZ6oNaW
        wvW4cfdw5mBMjG4CraGiO4QpJi7RMOqfltlgJMObQbgMPl2tHwvT6Z+eENU42dvZ
        JsgIuyoXG5XC5bZjRNmWy5hwk8+GCye8k6rD7Jr/2LYjK+8CIBY/mmq/QUKOeJpy
        ixvQaCswZA6DAAtrUwXZrgM4CCWQJFLAIwNyqJD7mOVJpTDj2rjczqws0cSWuC8D
        jJk4fOXNURjh/RDp7JP+KXoYEQ69YQfrmpOsHSxNwxzYkGrOukMhKLZUY9pmtFT8
        AqQhGJOSy+Yo1NcL4Fcxw8NZQYqoVkazYzHag5+lEC0IIAbUJXi5KiGf6j3Vk7LB
        =Q+xi
        -----END PGP MESSAGE-----

{% endif %}

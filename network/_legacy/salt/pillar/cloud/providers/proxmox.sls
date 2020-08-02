#!jinja|yaml|gpg

cloud:
  providers:
    proxint:
      driver: proxmox
      url: prox.lustfield.net
      host: prd-prox-01
      verify_ssl: False
      image: 'local:vztmpl/debian-9.0-standard_9.3-1_amd64.tar.gz'
      script: proxint_deploy
      user: |
          -----BEGIN PGP MESSAGE-----

          hQIMA9RfKrevXiv4ARAAqI7xhc9lbwZKFeuV7Q4E06MlvZpqCRf+v2q7X4NOBD6g
          5JqvO/TU22WnEzNwHAxqcvvh4cb0vrjlL5L1NjFTsn57pLV3sFfYxqLykS4XpPId
          CASUBZT/EsO1i3FAk0SmA2tFFJMYUI0Iqst4WGpx13PuygqWPQ78mkTKK89FRLSf
          SAEztMDbMHRhQoVN72h4hB86gb1JXpB/QLqhQTgUsbbvCEUQP36pdglNwsWpQ8mt
          TIo0M62BGYmDCZu/NWEPK82bn7hyp9j8Kg==
          =ZqMr
          -----END PGP MESSAGE-----
      password: |
          -----BEGIN PGP MESSAGE-----

          hQIMA9RfKrevXiv4AQ/+N6heDjlWhugumL2C5Y6GOKKKLW1svdDhg92zYzXenh7P
          0pMkcYo+ZzPnnKPkc1v/2hVUCWfqFOapj5lPzSGe79fghvUaLCEXSUEvTZYRV3lw
          dJTTg+fcGAyhI+wF4UbMC0onZYLQ9MsfzXunpUc2kbGWWQdQQNLWBWdQGkRIsWD4
          nSAxOijvl+mu6AVYkbx1TFf2SD4Sej4WzSL9M+8BZSSVXZOLtV+XXRxPkktW/xpN
          2dVvV8YeH+3U70fuQhkHAWmjH5FWi5vSPj2wwJJ2G7evSQ4LaKMeG2ECn05uQ4LS
          XAFxfRzDB1cnbySqmOELKU5sE9NCUUxTSbzadrMl/w9Xb0GXU6r6wDpdheVxSiW2
          0E3pDWXoXfQvvk6nhVsDkg+ume/JiMbw/P/MhrId6lmtioswdINhjegBjOQP
          =EIY0
          -----END PGP MESSAGE-----
      pubkey: 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDF3JIOM6aqF3jKTfLCiNEDdO59uxSghDcj5j2o6BN3SDZB1BTBYGW/1x3DpUdU5c2VK+Alhmswz23eVyX9AjezzUoU14Dfgfc0Uuwi2X/kabbnErqteO6xhANrn8KtDmujeg63oPCqQRpebE+KSMgSBiwzE64SiKdhYmGR8JFbHS9/H0KR7/NbgfxykOoDcWtQ4zBM3ShxJiapjM9I1s/yeJA/doh2bPZFCm5TUiefZjWZ7VeLEbUR5it7C398AlM2r7q/AyOYem3j+gz/I3ELb48bBCe+NWrzsxeJ+fg5mtXkLjzUL7uJwsoG2lXPaf5M+0KlVKllQLjhm1B79lVu/98WHkDupUQd/cb5wNI9+xYmpfTF4hEucKbaNNME34Yk5MWZOaLNflf9KeFDmnPCjTeQxIhJmXOIb1dW5YuTw/gZoRanXoo13u2m9lXg8YNfvENVTub9HeXM3XTEQbO1+nT/eBYf2YyN9PHoVgYpWJNvw5/estpsddeO1QHW0I+pOipbtPNSE3oqULfFtINCzzbE0oLJMhk3yL+F72AJdZCvetnImRO7CP0ivR3Du5roW8pTriT6/WfKxCn0UcIalAk8oELWjtBtRnOkQ4B9FdG0CptrRU8XXOxX4c6gLeSDtvgYs2AgYJXYZw/VNAXXUeZCe8ZkHy7rEwRm+s1UbQ== root@salt'

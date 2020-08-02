#!jinja|yaml|gpg
{# Custom SSH Keys for root #}
{% if salt.match.glob('prd-boot-*.core.lustfield.net')
      or salt.match.glob('prd-netbox-*.core.lustfield.net') %}
root_ssh_keys:
  pubweb:
      pub: |
          ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC3VECpohIFlvZVWjcM5U5aPytsVwRxJeElmfHcEEu3P42wKunjFPjtnYYmHKZC2RDxgaVqsPzR39u1yxPidg3izdBz69O4KeJF4X6xRrDNw26l4BOh7s8C69yIpJ9kQR5NRjwPdR1G94tXNTqWWu0TA6YjNHPPh1z21jG0+AekVUEKJtCc8lzbSqnMSGWrwPE8azFZk5Xz/b08Qy8z7vVtbR6Gl72SiCAxM2ydqvpnwje/ALLnBa45deCRaMPtObPbpvDzU0RbL+2wyxUKxm0dOnuv7w== anonymous@salt
      prv: |
          -----BEGIN PGP MESSAGE-----
          Version: GnuPG v1

          hQIMA9RfKrevXiv4ARAAqysA0BbD2J1CQvl8iULPohMGw8sU6+JwfEAVMm6E0G7h
          BtsXbTzuH3es2Mn+C7ZSXk8gSDIP6iIua+5nD3wu4ExYnOu2RhRFBNKzXn5dTJLe
          DpgsD4S3UrR5vcr5nlddQSsjsNSVhZTd+lj7hPvXFnHT2SN8jN4O+GF9+sF8RN2o
          xgXzKJCf1hIuqppm0LCgyngn2PMqs3MJeXgTZI4cDoN5XTGF2y+c5Gb8yvcXf28g
          MXcwpgV1Jhm2x9yhKIIDmvHvM3RoattlWl2TSUN+xKEl3quu/912FeBm49mzcqjQ
          Id0vQYWIBY3Cqt98IFyZooFbyLo1R7TXEHH5W9V1SoRMGfEk1mZj72dAO5HK0qiO
          DmlDYxhzBtWGjdwkq9pL8FRXzcgy+eCaXXDL6/yZai29lprshyYVhqIyGLqV4+dh
          75AJ+6yGg2isdgrUxlOy74Yydb8wRUQfs8fqfa9hBmn0wS9CdY7YuEl29ZBMXjG4
          1Uzv0Uk39zCY0Qg/QOhrnnTKExTY80Np8b4yr0r+ed8w10e9GKzLBa9zbgYaEUr0
          5ChchB0RTOiVfgOmrOvku3dG0FLHD/A4KXXaIDnqdk4J9ArTOBWj1Mw6OkKV9sAF
          bxcE0Ei9BVwXfKT1GCghJG7yT+NKy/mUvZLSDLLL6j/HsZeG93fpVmNPjX2MjTON
          Vzebu0QlyTXaogktBZ2w2RFvvrHbreW3/v8QwX51Ft9LQxTaJyMFt/KQQ/CO3rzK
          3ttEfpgk6Rdxse50zrOpZYwkeqKx5wDNjH9nEQWmOrHygNARXxuZP4fDKalUXpIG
          d68BFMQogzeHE2URsTApH3lVsVvbqUkXjoBwOP+CY8BB9C5oroXNffayTXDPzZ56
          CaEnCMBl5I6xH9ns+wZxbKAwowRLISbT8kvzPGVHFYhmeGbSXTPD5NO2WGLSnkwg
          IEV8h+Wa0FRxqAqqzX/CRGRLxzpUU5j28yIZQBhSFGlFcAszC2JS29SxKlbzCPQV
          lBUTOfQNVCPmOBHO5H3wXqKOHsKq3kjQpQ+fadOa+YZehrA1ksjdCqHaT4L37dIg
          OFYc4f96uxlfZM1X/Ckz8unVvtwdf/r3PcFfoQ+am4o5B9mXxcKqZgqL4rjvum7d
          f18=
          =FP+o
          -----END PGP MESSAGE-----

{% elif salt.match.glob('salt*') %}
root_ssh_keys:
  salt:
    - pub: |
        ssh-rsa AAAAB3NzaC1yvi3CokxWy9aoSPkU4rV76JVwzMzStfHJ6YqugNEd0CtIODRbrhLAOeqx4FhsW+wEP1Og3GzcDGvHldLTnVMxb0IOSmCqf0S9sTbpCsAuZjk8pYNrFMFoMz+F6uq+Ft4lSqJf25d+oEGOe12c5q7a9SfM7lA/zzdm//jgR6sb70PLTRWC7Nz5mRH1BOkSb02vRGF0HymPQqZYwFLjWDG69OWaErpuLZTjxHy/uRlq450BtfZLnLnt/bD4JA45bnXaOqRaYG0P59yQ1wGAFogyZlfKLMN8qqbTRvluBKte5rDM2FV0rn4hju+Aa++zYcAgr4nMYm4kmmNLJDLS7UO2Kete4qBqFfO0/4sOhMpdiUWGnw6t4ZlauWGkG9tw9J0xNZGSBTYIgtRGDc5SN5qbC+0iqIQ0jsHv9o3cpabjsF1+9tToC2STPi+VeQuIU86qFFcD0brIMzzJPM2ocn0PiSdkpjEuH5z3OXnP1QT9e2LgXPwfISUN5N0DQVzrvK4AjGfmF+j0Fu4N0rBkXBgMzTPNL54N+3CQ2jAuNtiYlQrsTiX/E/iTYbj4SpE9EJilScKZYg12CYynQtB7mG0hACTzz0D5Sp8wZBMfJjQKKeFbzIisIeNgVQw6Q== tmp@panther
      prv: |
          -----BEGIN PGP MESSAGE-----
          Version: GnuPG v1

          pX0FUo63jnHsVNCAI+j9sYMgcvmEYxe6nJ6LLIzlksDoq8Hm4jUKUfLOYgChpJDq
          VtakByfKbU7auzgDOMSfCI3rSSzeiKoTA+ujliEwbRW1wW1RCmJ1ugpXiwWXHDb4
          zlMMqWovgUxC6+EzSF2ecvQdvKtjJmLs/UYqzqfbmopJzXsyIAuGgQKB2uRD1OqM
          HnpH8nP+2ap2axLf13IuXHyKJL5OLBTbUhj2HljpnWI6Cl0ueXm+RPdX/wsGLxGN
          /dyg2bnryeas0smGqZpslMAzBF2BW7JHCNYII0qI6mrB23szB2uIzNSvxqB/zW1o
          EzJnXlvlST3gkbAomO+NNTnNj4sKMe7ju/r+MoT4un3520jJFybDKAW4jXeHCX7h
          oEQ2SLjQKe1d+7H+SAV9MWSunUR/QLp5e23oXQcP3uXFwTH+gahbR6NgN3CuE0YT
          kl1AJx74WtCBOCNKvFMeffcmE6bfoa+eQ4BK9LRPZ9Pdf1XHT3U5ydsOpUHIQ6Uh
          dqMVWOQ3VUwhTinFTpL9zrCf8ZFjM5FZ2Uft/F07s6oSSyrRvSx+Sp0oYSmvo8tp
          OO9HKa83JAykJkhLCo4PdR53pA84Tucb3F2g1mjmBbWGvDfeOi+56vOkhmx9np2q
          Qhcco4NIlPOySAJArXqtYZo8BUnBfEFfXe9L5VwH7M5kbZ0kA8W2kaQmDmv4kIg6
          MQOtqtFoIqaYt0g4FB6tYYvbXJyfKd2piceZnuvRlFROThB+EtkigXaeVM4GYdS8
          ZF1RLsYfMXwakscKrzwMSHJZwgmjnkehwYga/SWUC2K8VIR/UDbkGLidgLqzFrs3
          r3Z2P/QrxxUxju1h0GLGMqUBuqn+rByiGVw5LzxXHi5R+XB9vPz25VeGtKNWjxR8
          H6jIe8u3BCGlQcH7jh4DmRCiZI4kB8RuDNISY6ckKMBUWmJDg+IZizEmGBJeG2Xx
          MCQIjyqs7py0DMD6Fafc6LPVvlne78f9lWvvTD64SWASyap1rpxrVLCyxbiZxa1D
          PoDn6sZxVYfrqEAYUkdl8duZDbkCuWCBC92J8GDNvjRnBlSTL9oMn4pt/OIgMvtK
          L8Ziag==
          =ngk3
          -----END PGP MESSAGE-----
{% endif %}

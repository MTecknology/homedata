#!jinja|yaml|gpg
cloud:
  providers:
    lin:
      driver: linode
      ssh_key_names: root@salt
      ssh_key_file: /root/.ssh/id_rsa
      password: |
          -----BEGIN PGP MESSAGE-----

          hQIMA9RfKrevXiv4ARAArbU5XVQNOWnf2+g5qrSRtzdoXhWqGD6rjXbCHyKHEdFY
          vrfPzACinYY67EWSKEoj3uv4rxsdURoiwJZgiRJvRCMzh7ebfZyt2kiQDBWgKzEQ
          BmJXpKE2wpfLJMO+W+/azALbQP0hikIahAdp9wY4rtTn8qUgDaOMNy5UMV8/p+jf
          rF4Rm8StPMM5mH6xb22M8MopiMTyX+x4pvz9yKf04P1uoJZqzdi6JeN++qjwevJ0
          ZQHbAx9fBlq4skOKHloRwZMqlGHmnJFK4fmAkwmHNcO9JyqdV3uBnECSZpMQ68+b
          T74vpgMP2Itc6WqyuPDQ1654OWFKdj/KRbXcR6ChDahlXiflhgjscqeKBK71PNGj
          snC111Af
          =NcWu
          -----END PGP MESSAGE-----
      image: 'Debian 9'
      size: 'Nanode 1GB'
      location: 'Dallas, TX, USA'
      private_networking: False
      ipv6: True
      backups_enabled: False
      script: ovpn_deploy
      creat_dns_record: False
      apikey: |
          -----BEGIN PGP MESSAGE-----

          hQIMA9RfKrevXiv4AQ//dlz0AJpSnOXd8HW+4DfNkg24XbG/eAxm5U6zn5xPO9d6
          5HBmMCUymBFoHSzyVAuMY09i0lq5kOEhJf/9SImG2AzVYWZvsu5d6u+FTwXma848
          KNLmgp2D8hKQIJ2T5qdf/vO1mMf1YNRbi8ZSlP64audTU7Sa5pSevV+vhBDrLd4S
          ewEqiHkqYE/NEwW0HjMwlqsR/wLvsXKo5Sz7gMKdP9zjdt0aFrqldfJThsPQXkoN
          Nqvv8UEEm46rhttihREGwT8q4TXXlsHBQrX0hhi1Y5x/nVpLmGppRaQNDvmdNwdc
          D4MncPjugRTPsyjyJopFhFYzfKMZt1/nFrEoEw==
          =1VIf
          -----END PGP MESSAGE-----

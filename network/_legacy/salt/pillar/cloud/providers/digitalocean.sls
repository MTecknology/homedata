#!jinja|yaml|gpg
cloud:
  providers:
    do:
      driver: digitalocean
      ssh_key_names: root@salt
      ssh_key_file: /root/.ssh/id_rsa
      image: '9.5 x64'
      private_networking: False
      ipv6: True
      backups_enabled: False
      script: ovpn_deploy
      creat_dns_record: False
      personal_access_token: |
          -----BEGIN PGP MESSAGE-----

          hQIMA9RfKrevXiv4AQ//bULvgqrUKo+Cy99w9vU3ZysxcgV82Os5sB0ZuOHAMD8H
          e5IAK5OaRPAviUrW6rH9egl6circwuqPjB4h9y+2vnoH64jJBEw60CKKAahi2rng
          WseZ+o2hip24fIwQeiQGJOAlbTvSS517pUk4WUMGABpUO+ZLLQOU5ztnvEF0oczU
          PJBZcYM3KsvFTnGMASpX+M+SYEfbcTjjoYDAncjtT6MuIUkG65GlCd2WmoM0AyTS
          cwF3Bpk/IQbY5wtER8M1g7TYVaDy3U5k8xr0E1VuUM9jlk/NHraXUHMSbQd1YMkl
          q80guCyqSka91YXwsirKSukUG+uKgmzLk8t6szU0PuAGf3cNgtzRm4EIul+8s0zo
          MJl6JiIqexHmz6fjxxdWu96Bx+E=
          =VoL1
          -----END PGP MESSAGE-----

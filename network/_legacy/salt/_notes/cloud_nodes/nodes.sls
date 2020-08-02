salt-cloud:

  defaults:
    digitalocean:
      image: "8.7 x64"
      location: "New York 3"
      size: 512MB
    proxint:
      image: slowdisk:vztmpl/debian-8.0_Lustfield.tar.gz
      disk: slow;8
      type: lxc 
      host: prox1
      onboot: 1
      swap: 0
      cpu: 2
      mem: 256 

  digitalocean-nodes:

    oob-c1.domain.tld:
      id: oob-c1

    pbin.ngx.cc:
      id: pbin

    irc.domain.tld:
      id: irc 

    pubweb00.domain.tld:
      id: pubweb00

    pubweb02.domain.tld:
      id: pubweb02
      location: "Singapore 1"

  proxint-nodes:

    forge.domain.tld:
      id: 210;forge
      type: qemu
      mem: 256-8192
      cpu: 16
      disk: slow;64
      iface:
        net0:
          name: eth0
          vlan: 2

    {## 
     # PROD
     ##}

    boot.domain.tld:
      id: 101;boot
      mem: 512 
      cpu: 1
      disk: fast;8
      iface:
        net0:
          name: eth0
          vlan: 57
          ipv4_addr: 10.41.57.10/24
          ipv4_gw: 10.41.57.1

    salt.domain.tld:
      id: 111;salt
      mem: 2048
      cpu: 8
      disk: crypt;16
      iface:
        net0:
          name: eth0
          vlan: 50
          ipv4_addr: 10.41.50.11/24
          ipv4_gw: 10.41.50.1
          ipv6_addr: 2001:dead:b33f:50::11/64
          ipv6_gw: 2001:dead:b33f:50::1

    git.domain.tld:
      id: 112;git
      mem: 2048
      cpu: 4
      disk: crypt;32
      iface:
        net0:
          name: eth0
          vlan: 50
          ipv4_addr: 10.41.50.12/24
          ipv4_gw: 10.41.50.1
          ipv6_addr: 2001:dead:b33f:50::12/64
          ipv6_gw: 2001:dead:b33f:50::1

    log.domain.tld:
      id: 113;log
      mem: 512
      disk: crypt;64
      iface:
        net0:
          name: eth0
          vlan: 50
          ipv4_addr: 10.41.50.13/24
          ipv4_gw: 10.41.50.1
          ipv6_addr: 2001:dead:b33f:50::13/64
          ipv6_gw: 2001:dead:b33f:50::1

    apt.domain.tld:
      id: 114;apt
      mem: 1024
      disk: fast;16
      iface:
        net0:
          name: eth0
          vlan: 50
          ipv4_addr: 10.41.50.14/24
          ipv4_gw: 10.41.50.1
          ipv6_addr: 2001:dead:b33f:50::14/64
          ipv6_gw: 2001:dead:b33f:50::1

    [...]

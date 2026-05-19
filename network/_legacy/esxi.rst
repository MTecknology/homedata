ESXi Host
=========

ESXi was used for a short period of time and ultimately dismissed because VMFS5
is still essentially FAT and prone to corruption on power failure.

ESXi Installation
-----------------

- Download ESXi
- Set up HW-RAID
- Install ESXi
- Setup

  + ConfigureNetwork Management

    * Network Adapters: vmnic2 (tertiary card)
    * IPv4: 10.41.7.4X/24
    * IPv6: Disabled
    * DNS: 10.41.7.1
    * Hostname: virt1

- Log in to Web UI
- Disks: ssd, hdd
- Network: vSwitch1-Guest:

  + Both links
  + 2_Standard
  + 3_Guest
  + 50_Production
  + 51_DMZ
  + 7_Infrastructure

- Upload Debian ISO
- Assign License

New Template
------------

- New VM:

  .. code-block:: yaml

     Name: TEMPLATE.lustfield.net
     Guest Family: Linux
     OS Version: Latest Debian 64-bit
     CPU: 2
     Mem: 2G
     HD: 16G
     Net: 3_Guest
     CD: ISO/Debion

- Boot to Debian ISO

- Advanced > Expert install

  + Accept defaults, except:

    ^ Hostname: TEMPLATE
    ^ Domain: lustfield.net
    ^ Root Pass: $firstPassEver
    ^ User: Michael [...]
    ^ NTP: 10.41.7.1
    ^ TZ: Central
    ^ Manual Partition::

        /dev/sda  [msdos]
             sda1 [lvm]

        lvm [name:sys]:
            root  5G    ext4  /         3%
            home  100M  ext4  /home     0%
            boot  1G    ext2  /boot     2%
            var   1G    ext4  /var      5%
            log   1G    ext4  /var/log  5%
            opt   1G    ext4  /opt      1%
            srv   1G    ext4  /srv      1%

    ^ initrd: targeted
    ^ tasksel: de-select all
    ^ Execute shell::

        apt install vim wget openssh-server open-vm-tools screen rsync
        apt purge vim-tiny nano systemd
        apt install sysvinit-core
        apt purge dbun 'libdbus*'
        mkdir /root/.ssh
        wget https://p.lustfield.net/mteck.pub -O /root/.ssh/authorized_keys
        chmod 700 /root/.ssh
        chmod 600 /root/.ssh/authorized_keys
        echo 'PermitRootLogin without-password' >>/etc/ssh/ssh_config
        echo 'AllowGroups ssh-user' >>/etc/ssh/ssh_config
        groupadd -g 990 ssh-user
        usermod -a -G ssh-user michael
        vim /etc/gai.conf

  + Let proceed as usual
  + DO NOT reboot into new system

- Upgrade VM Compatibility
- Turn into Template

  + Export > OVF

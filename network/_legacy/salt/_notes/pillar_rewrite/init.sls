michael@arctic:~/repos/salt-pillar$ cat sys/pkgs/init.sls 
include:
  - sys.pkgs.acmetool
  - sys.pkgs.acng
  - sys.pkgs.postgresql
  - sys.pkgs.salt
  - sys.pkgs.sphinxsearch
  - sys.pkgs.tftpd
  - sys.pkgs.udev
  - sys.pkgs.versions




$ cat sys/pkgs/acmetool/init.sls
{% include 'sys/pkgs/acmetool/' ~ salt['mt_utils.app_group_from_id'](grains['id']) ~ '.sls' ignore missing %}

$ cat sys/pkgs/acng/init.sls
{% include 'sys/pkgs/acng/' ~ salt['mt_utils.app_group_from_id'](grains['id']) ~ '.sls' ignore missing %}

$ cat sys/pkgs/postgresql/init.sls
{% include 'sys/pkgs/postgresql/' ~ salt['mt_utils.app_group_from_id'](grains['id']) ~ '.sls' ignore missing %}

$ cat sys/pkgs/salt/init.sls
{% include 'sys/pkgs/salt/' ~ salt['mt_utils.app_group_from_id'](grains['id']) ~ '.sls' ignore missing %}

$ cat sys/pkgs/sphinxsearch/init.sls
{% include 'sys/pkgs/sphinxsearch/' ~ salt['mt_utils.app_group_from_id'](grains['id']) ~ '.sls' ignore missing %}

$ cat sys/pkgs/tftpd/init.sls
{% include 'sys/pkgs/tftpd/' ~ salt['mt_utils.app_group_from_id'](grains['id']) ~ '.sls' ignore missing %}

$ cat sys/pkgs/udev/init.sls
{% include 'sys/pkgs/udev/' ~ salt['mt_utils.app_group_from_id'](grains['id']) ~ '.sls' ignore missing %}



michael@arctic:~/repos/salt-pillar$ ls sys/pkgs/postgresql/
init.sls  prd_netbox.sls

michael@arctic:~/repos/salt-pillar$ ls sys/pkgs/sphinxsearch/
init.sls  prd_pubweb.sls

michael@arctic:~/repos/salt-pillar$ ls sys/pkgs/acng/
init.sls  prd_apt.sls  dev_apt.sls

michael@arctic:~/repos/salt-pillar$ ls sys/pkgs/tftpd/
init.sls  prd_pxe.sls  dev_pxe.sls  prd_fserv.sls

michael@arctic:~/repos/salt-pillar$ ls sys/pkgs/udev/
init.sls  prd_oobbeacon.sls

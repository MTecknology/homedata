Debian's LemonLDAP-NG
=====================

Created and retired...time has shown this was a better choice. :(

Install packages:

  .. code-block:: sh

    apt install screen lemonldap-ng lemonldap-ng-uwsgi-app nginx uwsgi certbot \
       libdpkg-perl libio-socket-ssl-perl libdigest-hmac-perl libcrypt-u2f-server-perl \
       libglib-perl liblasso-perl debian-keyring

Special plugin: ``debian-sso``

Backports: ``libio-socket-ssl-perl`` ``lemonldap-ng``

Initial config edits::

    /var/lib/lemonldap-ng/conf/lmConf-1.json
      s/example.com/debian.org/
      s/auth./llng-dev/
      s/reload./reload.llng-dev/
      s/manager./manager.llng-dev/
      s/http/https/

Web server configs:

  .. code-block:: sh

    rm /etc/nginx/sites-enabled/default
    cp /etc/lemonldap-ng/handler-nginx.conf /etc/nginx/conf.d/handler.conf
    cp /etc/lemonldap-ng/manager-nginx.conf /etc/nginx/conf.d/manager.conf
    cp /etc/lemonldap-ng/portal-nginx.conf /etc/nginx/conf.d/portal.conf

Edit: \*.conf

- Update domain name
- Update server_name
- Remove 'include ...lmlog.conf'
- Remove access_log
- Remove FastCGI
- Uncomment real_ip
- Uncomment uWSGI (include uwsgi_params;)
- lemonldap-ng-doc -> lemonldap-ng
- Add:

  .. code-block:: text

    location ^~ /.well-known/acme-challenge {
      alias /var/www/.acme-challenge;
    }

Edit: portal.conf

- Uncomment ssl_client_s_dn_cn  (s/fastcgi_param/uwsgi_param/)
- Move map out of server{}
- Add default_server:

  .. code-block:: sh

    certbot certonly --webroot -d llng-dev.debian.org
    certbot certonly --webroot -d manager.llng-dev.debian.org
    certbot certonly --webroot -d reload.llng-dev.debian.org

    ln -s /etc/uwsgi/apps-available/llng-server.yaml /etc/uwsgi/apps-enabled/llng-server.yaml
    service uwsgi restart

Edit: /etc/lemonldap-ng/lemonldap-ng.ini::

    [all]
    securedCookie = 1
    cda = 1
    [portal]

- ``service uwsgi restart``

Edit: /etc/hosts::

    127.0.0.1       auth.debian.net auth-manager.debian.net auth-reload.debian.net

Web Config
----------

.. code-block:: yaml

    Web Configuration:
    General Parameters
      Authentication:
        Authentication: LDAP
        Users: Same
        Password: None
        Registration: None
        LDAP Parameters:
          Connection:
            Server: ldaps://db.debian.org
            Port: 636
            BaseDN: dc=debian,dc=org
            Account: Empty
            Password: Empty
          Exported Variables:
            cn, gecos, ircNick, sn, supplementaryGid, uid
            (repeat in both columns)
          Filters:
            Default: (&(uid=$user)(objectClass=debianDeveloper))
      Issuer:
        OpenID Connect:
          Activation: On
      Cookies:
        Cookie Name: debsso
        Domain: debian.org
        Multiple Domains: On
        Secured Cookie: Secured Cookie (SSL)
    Variables:
      Macros:
        mail: $uid . '@debian.org'
    Virtual Hosts:
      manager.debsso.lustfield.net:
        Access Rule:
          Add:  or $uid eq "mtecknology"
    OpenID Connect:
      Issuer ID: debsso.lustfield.net
      Security:
        Keys: (click "New keys")
        Dynamic Registration: Off
      Exported vars for dynamic registration:
        cn, gecos, ircNick, sn, supplementaryGid, uid

Incomplete Tasks:

- email sending
- password reset
- Social Login
  + Username Checks
- Provide OIDC
- Provide SAML2
- Provide TLS

.. code-block:: text

    06:15 <yadd> Postgres with JSON support is the best choice
    -
    06:47 <yadd> The man who does it split portal in 2 pieces : auth.xxx and authssl.xxx for performances
    06:48 <yadd> https://lemonldap-ng.org/documentation/2.0/authssl#nginx_ssl_virtual_host_example_with_uwsgi
    -
    07:29 <yadd> NB: for GitLab, it is recommended to use SAML instead of OIDC

- https://lemonldap-ng.org/documentation/2.0/cda
- https://lemonldap-ng.org/documentation/2.0/ssocookie

guest-ldap
----------

.. code-block:: sh

    apt install slapd ldap-utils ldapscripts

PostgreSQL
----------

.. code-block:: sh

    apt install postgresql postgresql-client
    sudo -u postgres psql

.. code-block:: sql

    CREATE USER llng WITH PASSWORD 'eaMVrX5aC6NNyjsqB';
    CREATE DATABASE llngfederation;
    GRANT ALL PRIVILEGES ON DATABASE llngfederation TO llng;
    USE llngfederation;
    CREATE TABLE users(
        uid VARCHAR(30) PRIMARY KEY,
        username VARCHAR(30) UNIQUE NOT NULL,
        mail VARCHAR(250) NOT NULL,
        displayname VARCHAR(100) NOT NULL,
        firstname VARCHAR(100) NOT NULL,
        lastname VARCHAR(100),
        gpgkey TEXT,
        sshkey TEXT
    );

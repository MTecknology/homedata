Wireless Lan Controller
=======================

Follow: esxi/vm_template (for wlc.lustfield.net)

.. code-block:: sh

    apt install wget gnupg2 ca-certificates apt-transport-https dirmngr \ 
        gnupg software-properties-common multiarch-support

    apt remove dbus
    apt install wget

**OpenSSL**:

.. code-block:: sh

    wget http://security.debian.org/debian-security/pool/updates/main/o/openssl/libssl1.0.0_1.0.1t-1+deb8u12_amd64.deb
    dpkg -i libssl1.0.0_1.0.1t-1+deb8u12_amd64.deb

**MongoDB**:

.. code-block:: sh

    wget -qO - https://www.mongodb.org/static/pgp/server-3.4.asc | apt-key add -
    echo 'deb http://repo.mongodb.org/apt/debian jessie/mongodb-org/3.4 main' > /etc/apt/sources.list.d/mongodb.list
    apt update


**Java**:

.. code-block:: sh

    wget -qO - https://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public | apt-key add -
    echo 'deb https://adoptopenjdk.jfrog.io/adoptopenjdk/deb/ buster main' >/etc/apt/sources.list.d/java.list
    apt update
    apt install adoptopenjdk-8-hotspot
    echo 'JAVA_HOME=/usr/lib/jvm/adoptopenjdk-8-hotspot-amd64' > /etc/default/unifi

**Unifi**:

.. code-block:: sh

    apt-key adv --keyserver keyserver.ubuntu.com --recv 06E85760C0A52C50
    echo 'deb https://www.ui.com/downloads/unifi/debian stable ubiquiti' >/etc/apt/sources.list.d/unifi.list
    apt install unifi

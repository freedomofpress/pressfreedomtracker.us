Development
=============

Prerequisites
-------------

The installation instructions below assume you have the following software on your machine:

* `virtualenv <http://www.virtualenv.org/en/latest/virtualenv.html#installation>`_
* `docker <https://docs.docker.com/engine/installation/>`_
* `openssl <https://www.openssl.org/>`_ (required for ``cryptography``)*

OpenSSL Installation Note
-------------------------

If installing OpenSSL with Homebrew on macOS 10.7+, you will want to set
the following env vars in your shell profile (see this `GitHub comment <https://github.com/pyca/cryptography/issues/2692#issuecomment-272773481>`_):

.. code:: bash

    export LDFLAGS="-L/usr/local/opt/openssl/lib"
    export CPPFLAGS="-I/usr/local/opt/openssl/include"
    export PKG_CONFIG_PATH="/usr/local/opt/openssl/lib/pkgconfig"

Installation instructions
-------------------------

Clone the Git repository from ``git@github.com:littleweaver/pressfreedom.git``.

Run the following commands to get up and running:

.. code:: bash

    make dev-go #to launch containers
    make dev-attach-node #attach a shell to the node process
    make dev-attach-django #attach a shell to the python process

Once both of those terminals stop scrolling, you should be able to hit the
server at http://localhost:8000 . YAY

Resetting database
++++++++++++++++++

The containers are ephemeral so if you need to reset and start over simply kill
the containers and build them back up.

.. code:: bash

    make dev-stop
    make dev-go

Attaching to running containers
+++++++++++++++++++++++++++++++

So there are two ways to attach, the first is to attach to an actual running
process using the `make` commands listed under installation. The second, is to
connect to a container but land in a shell to run arbitrary commands. The
available containers are - `django`, `node`, and `postgresql`. To connect to one
and get a bash shell (for example the postgresql container):

.. code:: bash

    docker exec -it postgresql bash

Adobe Font Licenses
-------------------

Licenses for `Source Serif Pro <https://github.com/adobe-fonts/source-serif-pro>`_ and `Source Sans Pro <https://github.com/adobe-fonts/source-sans-pro>`_ are available at the paths below.

- `common/static/fonts/LICENSE.SourceSansPro.txt`
- `common/static/fonts/LICENSE.SourceSerifPro.txt`

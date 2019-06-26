.. image:: https://circleci.com/gh/freedomofpress/pressfreedom/tree/master.svg?style=svg&circle-token=e04b02d815f80dcf1194d55659573122ea7994f4
    :target: https://circleci.com/gh/freedomofpress/pressfreedom/tree/master

Development
=============

Prerequisites
-------------

The installation instructions below assume you have the following software on your machine:

* `docker <https://docs.docker.com/engine/installation/>`_
* `docker-compose <https://docs.docker.com/compose/install/>`_ OR
* `pipenv <https://docs.pipenv.org/#install-pipenv-today>`_

Note that you can either install docker-compose natively or via `pipenv`.
If you choose the pipenv route you'll need to run these commands:

.. code:: bash

    # Run this the first time you enter the directory
    pipenv install
    # Run this every other time
    pipenv shell

Local Development instructions
------------------------------

When you want to play with the environment, you will be using
``docker-compose``. Your guide to understand all the nuances of ``docker-compose``
can be found in the `official docs <https://docs.docker.com/compose/reference/>`_. To start the
environment, run the following your first run:

.. code:: bash

    # One-time command to run and forget
    make dev-init

    # Starts up the environment
    docker-compose up

    # Inject development data (also only needs to be run once)
    docker-compose exec django ./manage.py createdevdata

You should be able to hit the web server interface by running ``make open-browser``

Note: the ``createdevdata`` command fetches images from the internet
by default.  To disable this behavior, run the command with the
``--no-download`` argument, e.g.:

.. code:: bash

    docker-compose exec django ./manage.py createdevdata --no-download

To reset your database back to its initial state, I recommend removing the postgresql docker container and re-running the dev data command.  First, stop your containers by pressing control+c if they are running.  Then run these two commands.

.. code:: bash

    docker-compose rm -f postgresql && docker-compose up --build
    docker-compose exec django ./manage.py createdevdata

Debugging
---------

If you want to use the `PDB <https://docs.python.org/3/library/pdb.html>`_ program for debugging, it is possible.  First, add this line to an area of the code you wish to debug:

.. code:: python

    import ipdb; ipdb.set_trace()

Second, attach to the running Django container.  This must be done in a shell, and it is within this attached shell that you will be able to interact with the debugger.  The command to attach is ``docker attach <ID_OF_DJANGO_CONTAINER>``, and on UNIX-type systems, you can look up the ID and attach to the container with this single command:

.. code:: bash

    docker attach $(docker-compose ps -q django)

Once you have done this, you can load the page that will run the code with your ``import ipdb`` and the debugger will activate in the shell you attached.  To detach from the shell without stopping the container press ``Control+P`` followed by ``Control+Q``.

Updating Requirements
+++++++++++++++++++++

New requirements should be added to ``*requirements.in`` files, for use with ``pip-compile``.
There are three Python requirements files:

* ``requirements.in`` production application dependencies
* ``dev-requirements.in`` development container additions (e.g. debug toolbar)
* ``devops/requirements.in`` local testing and CI requirements (e.g. molecule, safety)

Add the desired dependency to the appropriate ``.in`` file, then run:

.. code:: bash

    make update-pip-dependencies

All requirements files will be regenerated based on compatible versions. Multiple ``.in``
files can be merged into a single ``.txt`` file, for use with ``pip``. The Makefile
target handles the merging of multiple files.

Advanced actions against the database
+++++++++++++++++++++++++++++++++++++

Database import
---------------

Drop a postgres database dump into the root of the repo and rename it to
``import.db``. To import it into a running dev session (ensure ``make dev-go`` has
already been started) run ``make dev-import-db``. Note that this will not pull in
images that are referenced from an external site backup.


Connect to postgresql service from host
---------------------------------------

The postgresql service is exposed to your host on port ``15432``. If you have a GUI
database manipulation application you'd like to utilize, your settings will be:

* username - ``tracker``
* password - ``trackerpassword``
* dbname - ``trackerdb``
* the host/port can be determined by running ``docker-compose port postgresql 5432``

Mimic CI and production environment
-----------------------------------

You can mimic a production environment where django is deployment with gunicorn,
reverse nginx proxy, and debug mode off using the following command:

.. code:: bash

    docker-compose -f prod-docker-compose.yaml up

All subsequent docker-compose files will need that explicit ``-f`` flag pointing
to the production-like compose file.

Database snapshots
------------------

When developing, it is often required to switch branches.  These
different branches can have mutually incompatible changes to the
database, which can render the application inoperable.  It is
therefore helpful to be able to easily restore the database to a
known-good state when making experimental changes.  There are two
commands provided to assist in this.

``make dev-save-db``: Saves a snapshot of the current state of the
database to a file in the ``db-snapshots`` folder.  This file is named
for the currently checked-out git branch.

``make dev-restore-db``: Restores the most recent snapshot for the
currently checked-out git branch.  If none can be found, that is,
``make dev-save-db`` has never been run for the current branch, this
command will do nothing.  If a saved database is found, all data in
database will be replaced with that from the file.  Note that this
command will terminate all connections to the database and delete all
data there, so care is encouraged.

Workflow suggestions.  I find it helpful to have one snapshot for each
active branch I'm working on or reviewing, as well as for master.
Checking out a new branch and running its migrations should be
followed by running ``make dev-save-db`` to give you a baseline to
return to when needed.

When checking out a new branch after working on another, it can be
helpful to restore your snapshot from master, so that the migrations
for the new branch, which were presumably based off of master, will
have a clean starting point.

Adobe Font Licenses
+++++++++++++++++++

Licenses for `Source Serif Pro <https://github.com/adobe-fonts/source-serif-pro>`_ and `Source Sans Pro <https://github.com/adobe-fonts/source-sans-pro>`_ are available at the paths below.

- `common/static/fonts/LICENSE.SourceSansPro.txt`
- `common/static/fonts/LICENSE.SourceSerifPro.txt`

Design decision notes
+++++++++++++++++++++

Search
------

The search bar on the site is a shortcut to using incident search.
This is because the site is primarily incident-related, and using incident search provides more powerful filtering as well as enhanced previews.
As a result, there is no generic wagtail search view which includes other content such as blog posts.
See https://github.com/freedomofpress/pressfreedom/pull/592.

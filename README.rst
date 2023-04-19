.. note::

   By contributing to this project, you agree to abide by our
   `Code of Conduct <https://github.com/freedomofpress/.github/blob/main/CODE_OF_CONDUCT.md>`_.

==========================
U.S. Press Freedom Tracker
==========================

.. image:: https://circleci.com/gh/freedomofpress/pressfreedomtracker.us.svg?style=svg
    :target: https://circleci.com/gh/freedomofpress/pressfreedomtracker.us


This is the code that powers the U.S. Press Freedom Tracker website. It is built with Wagtail and served at `pressfreedomtracker.us <https://pressfreedomtracker.us/>`_.


Development
=============

Prerequisites
-------------

The installation instructions below assume you have the following software on your machine:

* `docker <https://docs.docker.com/engine/installation/>`_
* `docker-compose <https://docs.docker.com/compose/install/>`_

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

    # NOTE: temporarily not available due to incompatibility with wagtail 2.7
    # Add wagtail inventory to search wagtail pages by block type
    docker-compose exec django ./manage.py block_inventory

You should be able to hit the web server interface by running ``make open-browser``

If you run into any issues starting the application locally, check the `troubleshooting doc <TROUBLESHOOTING.md>`_ for solutions to common problems.

Note: the ``createdevdata`` command fetches images from the internet
by default.  To disable this behavior, run the command with the
``--no-download`` argument, e.g.:

.. code:: bash

    docker-compose exec django ./manage.py createdevdata --no-download

To reset your database back to its initial state, I recommend removing the postgresql docker container and re-running the dev data command.  First, stop your containers by pressing control+c if they are running.  Then run these two commands.

.. code:: bash

    docker-compose rm -f postgresql && docker-compose up --build
    docker-compose exec django ./manage.py createdevdata

To test your frontend code with jest, you can run the following command:

.. code:: bash

    docker-compose exec node npm test

Debugging
---------

If you want to use the `PDB <https://docs.python.org/3/library/pdb.html>`_ program for debugging, it is possible.  First, add this line to an area of the code you wish to debug:

.. code:: python

    import ipdb; ipdb.set_trace()

Second, attach to the running Django container.  This must be done in a shell, and it is within this attached shell that you will be able to interact with the debugger.  The command to attach is ``docker attach <ID_OF_DJANGO_CONTAINER>``, and on UNIX-type systems, you can look up the ID and attach to the container with this single command:

.. code:: bash

    docker attach $(docker-compose ps -q django)

Once you have done this, you can load the page that will run the code with your ``import ipdb`` and the debugger will activate in the shell you attached.  To detach from the shell without stopping the container press ``Control+P`` followed by ``Control+Q``.

Debug Toolbar
+++++++++++++

Another debugging aid is the `django debug toolbar <https://django-debug-toolbar.readthedocs.io/en/latest/index.html>`_
It is disabled by default for performance reasons.  To enable it, add

.. code:: python

    ENABLE_DEBUG_TOOLBAR = True

To ``tracker/settings/local.py`` (you may need to create this file if it does not exist in your local working copy).  After reloading the page, there should be a tab in the upper-right corner of the page to open the toolbar.


Profiling
---------

There are a couple of options preconfigured in this repo for profiling the application.  They are `django-cprofile-middleware <https://pypi.org/project/django-cprofile-middleware/>`_, `silk <https://github.com/jazzband/django-silk>`_ middleware, and `pyinstrument <https://pypi.org/project/pyinstrument/>`_.

Profiling is not enabled by default, as it does add potential performance overhead if you don't actively need it.  To enable silk (and cprofile), set ``DJANGO_PROFILE=yes`` when starting docker compose.  To enable pyinstrument, set ``PYINSTRUMENT=yes``:

.. code:: bash

    PYINSTRUMENT=yes DJANGO_PROFILE=yes docker compose up

This will enable both middlewares.  To view the cProfile information for any url, append ``?prof`` to the url (or add it to an existing query string with ``&prof``).  This can give you fairly detailed information about which lines of code are causing your view to be slow.  Additional information about the information provided is available in `the Python documentation <https://docs.python.org/3.7/library/profile.html>`_.

Pyinstrument functions similarly to cProfile, but it has a much nicer interface.  Append ``?profile`` (or ``&profile``) to any URL to load it.

If the specific lines of python code are not enough to determine what's causing the slowdown, it might be the database.  To view more detailed profiling data about database queries, I recommend silk.  The silk middleware logs all queries generated on a per-request basis.  To see this, make a request to the view you want to profile, wait for it to complete, then load the silk admin at ``http://localhost:8000/silk``.



Dependency Management
---------------------

Adding new requirements
+++++++++++++++++++++++

New requirements should be added to ``*requirements.in`` files, for use with ``pip-compile``.
There are two Python requirements files:

* ``requirements.in`` production application dependencies
* ``dev-requirements.in`` local testing and CI requirements

Add the desired dependency to the appropriate ``.in`` file, then run:

.. code:: bash

    make compile-pip-dependencies

All requirements files will be regenerated based on compatible versions. Multiple ``.in``
files can be merged into a single ``.txt`` file, for use with ``pip``. The Makefile
target handles the merging of multiple files.

This process is the same if a requirement needs to be changed (i.e. its version number restricted) or removed.  Make the appropriate change in the correct ``requirements.in`` file, then run the above command to compile the dependencies.

Upgrading existing requirements
+++++++++++++++++++++++++++++++

There are separate commands to upgrade a package without changing the ``requirements.in`` files.  The command

.. code:: bash

    make pip-update PACKAGE=package-name

will update the package named ``package-name`` to the latest version allowed by the constraints in ``requirements.in`` and compile a new ``dev-requirements.txt`` and ``requirements.txt`` based on that version.

If the package appears only in ``dev-requirements.in``, then you must use this command:

.. code:: bash

    make pip-dev-update PACKAGE=package-name

which will update the package named ``package-name`` to the latest version allowed by the constraints in ``requirements.in`` and compile a new ``dev-requirements.txt``.


Advanced actions against the database
-------------------------------------

Database import
+++++++++++++++

Drop a postgres database dump into the root of the repo and rename it to
``import.db``. To import it into a running dev session (ensure ``make dev-go`` has
already been started) run ``make dev-import-db``. Note that this will not pull in
images that are referenced from an external site backup.


Connect to postgresql service from host
+++++++++++++++++++++++++++++++++++++++

The postgresql service is exposed to your host on port ``15432``. If you have a GUI
database manipulation application you'd like to utilize, your settings will be:

* username - ``tracker``
* password - ``trackerpassword``
* dbname - ``trackerdb``
* the host/port can be determined by running ``docker-compose port postgresql 5432``

Mimic CI and production environment
+++++++++++++++++++++++++++++++++++

You can mimic a production environment where django is deployment with gunicorn,
reverse nginx proxy, and debug mode off using the following command:

.. code:: bash

    docker-compose -f prod-docker-compose.yaml up

All subsequent docker-compose files will need that explicit ``-f`` flag pointing
to the production-like compose file.

Database snapshots
++++++++++++++++++

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
active branch I'm working on or reviewing, as well as for develop.
Checking out a new branch and running its migrations should be
followed by running ``make dev-save-db`` to give you a baseline to
return to when needed.

When checking out a new branch after working on another, it can be
helpful to restore your snapshot from develop, so that the migrations
for the new branch, which were presumably based off of develop, will
have a clean starting point.

Deployment
=============

*Important Note*: We want to make PFT customizable for organizations who
wish to deploy it as a tool for regions outside the US, but this work is
still in progress. Please see
https://github.com/freedomofpress/pressfreedomtracker.us/issues/647 for
the current status and how you can help.

Building
-------------

The development ``docker-compose`` setup includes separate application
and Node.js containers for hot-reloading purposes. To build a container
for production use, run:

.. code:: bash

    docker build --build-arg USERID=1000 -t TAG -f devops/docker/ProdDjangoDockerfile .

Running
-------------

This setup can also be tested locally with `docker-compose` by using:

.. code:: bash

    docker-compose -f prod-docker-compose.yaml up

This setup will configure the app with production-like settings. In
particular, `whitenoise` is used to serve static files.

Setup
-------------

When deploying the container to your actual production environment,
refer to the environment variables in ``prod-docker-compose.yaml``,
changing things appropriately:

- ``DJANGO_DB_*`` for your database
- Based on your deployment domain/hostname:
    - ``DJANGO_BASE_URL``
    - ``DJANGO_ALLOWED_HOSTS``
    - ``DJANGO_CSRF_TRUSTED_ORIGINS``
    - if applicable, ``DJANGO_ONION_HOSTNAME``
- If you are using a read-only filesystem, give these a path to a read-write tmpfs:
    - ``DJANGO_GCORN_HEARTBT_DIR``
    - ``DJANGO_GCORN_UPLOAD_DIR``
    - ``TMPDIR``
- Replace these dummied out secrets:
    - ``DJANGO_SECRET_KEY`` (generate a random one)
    - ``RECAPTCHA_*``
- Using an object storage service for media files is recommended; for Google Storage:
    - ``GS_BUCKET_NAME``
    - ``GS_CREDENTIALS`` (path to a JSON file)
    - ``GS_CUSTOM_ENDPOINT`` (if you have a CNAME pointing to your bucket)

This list is incomplete; please open an issues if you run into something
missing.

Adobe Font Licenses
===================

Licenses for `Source Serif Pro <https://github.com/adobe-fonts/source-serif-pro>`_ and `Source Sans Pro <https://github.com/adobe-fonts/source-sans-pro>`_ are available at the paths below.

- `common/static/fonts/LICENSE.SourceSansPro.txt`
- `common/static/fonts/LICENSE.SourceSerifPro.txt`

Design decision notes
=====================

Search
------

The search bar on the site is a shortcut to using incident search.
This is because the site is primarily incident-related, and using incident search provides more powerful filtering as well as enhanced previews.
As a result, there is no generic wagtail search view which includes other content such as blog posts.
See https://github.com/freedomofpress/pressfreedomtracker.us/pull/592.

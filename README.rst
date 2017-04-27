Development
=============

Prerequisites
-------------

The installation instructions below assume you have the following software on your machine:

* `Python 3.5.x <http://www.python.org/download/releases/3.5.0/>`_
* `Pip <https://pip.readthedocs.org/en/latest/installing.html>`_
* `virtualenv <http://www.virtualenv.org/en/latest/virtualenv.html#installation>`_ (optional)
* `virtualenvwrapper <http://virtualenvwrapper.readthedocs.org/en/latest/install.html>`_ (optional)
* `PostgreSQL <http://www.postgresql.org/>`_
* `Node.js <https://nodejs.org>`_
* `npm <https://www.npmjs.com/>`_

Installation instructions
-------------------------

Clone the Git repository from ``git@github.com:littleweaver/pressfreedom.git``.

Make sure to ``cd pressfreedom`` into the repo directory before following the next steps.

Python dependencies
+++++++++++++++++++

If you are using virtualenv or virtualenvwrapper, create and activate an environment. E.g.,

.. code:: bash

    mkvirtualenv -p python3.5 pressfreedom       # Using virtualenvwrapper.

Then install the requirements:

.. code:: bash

    pip install -r requirements.txt

If you encounter errors during ``pip install``, you may need to install build dependencies for some of the Python packages. Instructions for doing so are commonly found in the package's installation documentation (e.g. for `cryptography <https://cryptography.io/en/latest/installation/.>`_).

Front-end development
+++++++++++++++++++++

Install node dependencies for react / webpack.

.. code:: bash

    npm install
    npm run start

Database initialization
+++++++++++++++++++++++

Set the database url as the `DATABASE_URL` enviromnent variable.
The format for `DATABASE_URL` is
`<database_type>://<database_user>:<database_password>@<server>:<port>/<database_name>`

The first time you run, you'll need to run migrations and create a superuser:

.. code:: bash

    python manage.py migrate           # Create/sync the database.
    python manage.py createdevdata

`createdevdata` configures the database to resemble a first approximation of
the production site, which is useful for development. It also creates a default
super (username: **test**, password: **test**).

Get it running
--------------

If you are using virtualenv, ensure that you are in the appropriate virtual environment, e.g.

.. code:: bash

    workon pressfreedom                # Switch virtualenv.
    python manage.py runserver         # Run the server!

In another terminal, start webpack to monitor your frontend assets and automatically rebuild them when they update:

.. code:: bash

    npm run start

Then, navigate to ``http://127.0.0.1:8000/`` in your favorite web browser to view the site! Navigate to ``http://127.0.0.1:8000/admin/`` to edit pages.

Resetting database
++++++++++++++++++

If a change is made which changes test data or initial database migrations, simply do the following:

.. code:: bash

    python manage.py reset_db          # Make sure runserver is turned off first!
    python manage.py migrate

Getting some data
+++++++++++++++++

Load basic data with the following command:

.. code:: bash

    python manage.py createdevdata

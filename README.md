# U.S. Press Freedom Tracker

> [!NOTE]
> By contributing to this project, you agree to abide by our [Code of Conduct](https://github.com/freedomofpress/.github/blob/main/CODE_OF_CONDUCT.md).

This is the code that powers the U.S. Press Freedom Tracker website. It is built with Wagtail and served at [pressfreedomtracker.us](https://pressfreedomtracker.us/).

| Environment | Status                                                                                                                                   |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Production  | ![Production CI](https://github.com/freedomofpress/pressfreedomtracker.us/actions/workflows/check.yaml/badge.svg?branch=prod&event=push) |
| Development | ![Develop CI](https://github.com/freedomofpress/pressfreedomtracker.us/actions/workflows/check.yaml/badge.svg?branch=develop&event=push) |

## Development

### Prerequisites

The installation instructions below assume you have the following
software on your machine:

- [docker](https://docs.docker.com/engine/installation/) or
  [podman](https://podman.io/docs/installation), with "compose"
  support
- [just](https://github.com/casey/just)

### Local Development instructions

When you want to play with the environment, you will be using
`docker compose`. Your guide to understand all the nuances of
`docker compose` can be found in the [official
docs](https://docs.docker.com/compose/reference/). To start the
environment, run the following your first run:

```bash
# Starts up the environment (records your host UID in .env on the way,
# so a bare `docker compose up` works afterwards too)
just dev

# Inject development data (also only needs to be run once)
just createdevdata

# install pre-commit and set up hooks
pip install pre-commit
pre-commit install
```

You should be able to hit the web server interface by running
`just open-browser`:

```bash
just open-browser
```

If have problems starting the application locally, check the
[Troubleshooting](#troubleshooting) section below.

Note: the `createdevdata` command fetches images from the internet by
default. To disable this behavior, run the command with the
`--no-download` argument, e.g.:

```bash
docker compose exec django ./manage.py createdevdata --no-download
```

#### Working on dependencies in place

To work on any upstream dependency in-place during development, you can
clone the dependency into the `develop-pkgs/` subdirectory. When you
start the `django` and `node` containers after doing so, a Python
package (providing a `pyproject.toml`) will be installed editable, and
any Node package (providing a `package.json`) will be built and watched,
so they can be worked on in-place while running the full Press Freedom
Tracker Django project.

## Testing

### Running the tests

To perform a quick spot check to ensure all tests are passing you can
run:

```bash
just test
```

To quickly run Python linting you can use:

```bash
just lint
```

To test your frontend code with jest, you can run the following command:

```bash
just test-js
```

If tests need to be updated, you can run the following command:

```bash
docker compose exec node npm run test-update
```

## Troubleshooting

### Database Reset

To reset your database back to its initial state, run:

```bash
just reset-db
```

This removes the postgresql container and re-seeds it by running
`createdevdata`.

### Debugging

If you want to use the [PDB](https://docs.python.org/3/library/pdb.html)
program for debugging, it is possible. First, add this line to an area
of the code you wish to debug:

```python
import ipdb

ipdb.set_trace()
```

Second, attach to the running Django container. This must be done in a
shell, and it is within this attached shell that you will be able to
interact with the debugger. Run:

```bash
just attach
```

Once you have done this, you can load the page that will run the code
with your `import ipdb` and the debugger will activate in the shell you
attached. To detach from the shell without stopping the container press
`Control+P` followed by `Control+Q`.

#### Django Debug Toolbar

Another debugging aid is the [django debug
toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/index.html)
It is disabled by default for performance reasons. To enable it, add

```python
ENABLE_DEBUG_TOOLBAR = True
```

### Mimic production environment

You can mimic a production environment where django is deployed with
gunicorn, a reverse nginx proxy, and debug mode off using the
`prod-docker-compose.yaml` file. Note that build time for this
container takes much longer than the developer environment:

Run it via `just prod`, which builds the image first
(`just build-prod` builds alone):

```bash
just prod
```

All subsequent docker compose commands will need that explicit `-f` flag
pointing to the production-like compose file.

To `tracker/settings/local.py` (you may need to create this file if it
does not exist in your local working copy). After reloading the page,
there should be a tab in the upper-right corner of the page to open the
toolbar.

## Profiling

There are a couple of options preconfigured in this repo for profiling
the application. They are
[django-cprofile-middleware](https://pypi.org/project/django-cprofile-middleware/),
[silk](https://github.com/jazzband/django-silk) middleware, and
[pyinstrument](https://pypi.org/project/pyinstrument/).

Profiling is not enabled by default, as it does add potential
performance overhead if you don't actively need it. To enable silk (and
cprofile), set `DJANGO_PROFILE=yes` when starting docker compose. To
enable pyinstrument, set `PYINSTRUMENT=yes`:

```bash
PYINSTRUMENT=yes DJANGO_PROFILE=yes docker compose up
```

This will enable both middlewares. To view the cProfile information for
any url, append `?prof` to the url (or add it to an existing query
string with `&prof`). This can give you fairly detailed information
about which lines of code are causing your view to be slow. Additional
information about the information provided is available in [the Python
documentation](https://docs.python.org/3.14/library/profile.html).

Pyinstrument functions similarly to cProfile, but it has a much nicer
interface. Append `?profile` (or `&profile`) to any URL to load it.

If the specific lines of python code are not enough to determine what's
causing the slowdown, it might be the database. To view more detailed
profiling data about database queries, I recommend silk. The silk
middleware logs all queries generated on a per-request basis. To see
this, make a request to the view you want to profile, wait for it to
complete, then load the silk admin at `http://localhost:8000/silk`.

## Database management

### Connect to PostgreSQL

To connect to the database, use the following credentials:

- username - `tracker`
- password - `trackerpassword`
- dbname - `trackerdb`
- the host/port can be determined by running
  `docker compose port postgresql 5432`

### Database import

Drop a postgres database dump into the root of the repo and rename it to
`import.db`. To import it into a running dev session (ensure `just dev`
has already been started) run `just import-db`. Note that this will not
pull in images that are referenced from an external site backup.

### Database snapshots

When developing, it is often required to switch branches. These
different branches can have mutually incompatible changes to the
database, which can render the application inoperable. It is therefore
helpful to be able to easily restore the database to a known-good state
when making experimental changes. There are two commands provided to
assist in this.

`just save-db`: Saves a snapshot of the current state of the database to
a file in the `db-snapshots` folder. This file is named for the
currently checked-out git branch.

`just restore-db`: Restores the most recent snapshot for the currently
checked-out git branch. If none can be found, that is, `just save-db`
has never been run for the current branch, this command will do nothing.
If a saved database is found, all data in database will be replaced with
that from the file. Note that this command will terminate all
connections to the database and delete all data there, so care is
encouraged.

Workflow suggestions. I find it helpful to have one snapshot for each
active branch I'm working on or reviewing, as well as for develop.
Checking out a new branch and running its migrations should be followed
by running `just save-db` to give you a baseline to return to when
needed.

When checking out a new branch after working on another, it can be
helpful to restore your snapshot from develop, so that the migrations
for the new branch, which were presumably based off of develop, will
have a clean starting point.

## Dependency Management

### Adding new requirements

New requirements should be added to `*requirements.in` files, for use
with `pip-compile`. There are three Python requirements files:

- `requirements.in` production application dependencies
- `dev-requirements.in` local testing and CI requirements
- `ci-requirements.in` additional tooling used only in CI (coverage
  diffing, testinfra)

Add the desired dependency to the appropriate `.in` file, then run:

```bash
just pip-compile
```

All requirements files will be regenerated based on compatible versions.
Multiple `.in` files can be merged into a single `.txt` file, for use
with `pip`. The just recipe handles the merging of multiple files.

This process is the same if a requirement needs to be changed (i.e. its
version number restricted) or removed. Make the appropriate change in
the correct `requirements.in` file, then run the above command to
compile the dependencies.

### Upgrading existing requirements

There are separate commands to upgrade a package without changing the
`requirements.in` files. The command

```bash
just pip-compile --upgrade-package=package-name
```

will update the package named `package-name` to the latest version
allowed by the constraints in `requirements.in` and compile a new
`dev-requirements.txt` and `requirements.txt` based on that version.

If the package appears only in `dev-requirements.in`, then you must use
this command:

```bash
just pip-compile-dev --upgrade-package=package-name
```

which will update the package named `package-name` to the latest version
allowed by the constraints in `requirements.in` and compile a new
`dev-requirements.txt`.

## Managing CMS Content

You can log in to the Wagtail interface at `/admin` with the following
credentials:

- username - `test`
- password - `test`

## Deployment

_Important Note_: We want to make PFT customizable for organizations who
wish to deploy it as a tool for regions outside the US, but this work is
still in progress. Please see
<https://github.com/freedomofpress/pressfreedomtracker.us/issues/647>
for the current status and how you can help.

### Building

The development `docker compose` setup includes separate application and
Node.js containers for hot-reloading purposes. To build a container for
production use, run:

```bash
docker build -t TAG -f ci/containers/Containerfile --target prod .
```

and for the chart pregenerator service:

```bash
docker build -t TAG -f ci/containers/Containerfile --target chartgen .
```

### Running

This production build can also be tested locally with `docker compose`;
see [Mimic production environment](#mimic-production-environment) above.
This setup will configure the app with production-like settings. In
particular, `whitenoise` is used to serve static files.

### Setup

When deploying the container to your actual production environment,
refer to the environment variables in `prod-docker-compose.yaml`,
changing things appropriately:

- `DJANGO_DB_*` for your database

- Based on your deployment domain/hostname:
  - `DJANGO_BASE_URL`
  - `DJANGO_ALLOWED_HOSTS`
  - `DJANGO_CSRF_TRUSTED_ORIGINS`
  - if applicable, `DJANGO_ONION_HOSTNAME`

- If you are using a read-only filesystem, give these a path to a read-write tmpfs:
  - `DJANGO_GCORN_HEARTBT_DIR`
  - `DJANGO_GCORN_UPLOAD_DIR`
  - `TMPDIR`

- Replace these dummied out secrets:
  - `DJANGO_SECRET_KEY` (generate a random one)
  - `RECAPTCHA_*`

- Using an object storage service for media files is recommended; for Google Storage:
  - `GS_BUCKET_NAME`
  - `GS_CREDENTIALS` (path to a JSON file)
  - `GS_CUSTOM_ENDPOINT` (if you have a CNAME pointing to your bucket)

This list is incomplete; please open an issues if you run into something
missing.

## Design decision notes

### Search

The search bar on the site is a shortcut to using incident search. This
is because the site is primarily incident-related, and using incident
search provides more powerful filtering as well as enhanced previews. As
a result, there is no generic wagtail search view which includes other
content such as blog posts. See
<https://github.com/freedomofpress/pressfreedomtracker.us/pull/592>.

## Other Commands

### just

In order to ensure that all commands are run in the same environment, we have added a `just lint` command that checks Python code (`ruff`), SASS (`stylelint`), SVGs (`svgo`), PNGs (`oxipng`). It also runs `bandit` and the migration check. This is done in the container, rather than on your local env.

Use `just ruff-fix` to apply ruff's fixes and formatting in place.

Run `just` on its own to list every available recipe.

### Management Commands

In addition to the management commands provided by [Django](https://docs.djangoproject.com/en/stable/ref/django-admin/) and [Wagtail](http://docs.wagtail.io/en/stable/reference/management_commands.html), the project has a set of its own custom management commands. All commands listed should be prefaced by `docker compose exec django ./manage.py`.

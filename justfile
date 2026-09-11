# Recipes for developing and testing the pressfreedomtracker.us website.
# Run `just` (or `just --list`) to see everything available.
#
# Container engine: prefers docker for backwards compat.
# Override explicitly with `CONTAINER_ENGINE=podman just <recipe>`.

engine := env_var_or_default("CONTAINER_ENGINE", "docker")
compose := engine + " compose"
# Must stay in step with PYTHON_IMAGE in ci/containers/Containerfile: pip-compile
# resolves hashes against this interpreter, and the app installs the result. The
# tag alone is not enough -- Docker Hub rebuilds it in place for patches, so
# without the digest the two can silently drift apart.
python_builder := "docker.io/library/python:3.14.6-slim-trixie@sha256:44dd04494ee8f3b538294360e7c4b3acb87c8268e4d0a4828a6500b1eff50061"

# pinning a specific, recent version of pip-tools, so that the dev-env
# reuses the same tooling predictably.
# TODO: drop use of pip-tools in favor of more modern python package management.
pip_tools_version := "7.6.1"

# Show available recipes.
default:
    @just --list

# Write the host UID into .env so containers build/run as your user (see README).
dev-init:
    echo "UID=$(id -u)" > .env

# Same, but non-destructive: every compose invocation interpolates ${UID:?err},
# so recipes depend on this to work from a cold checkout without clobbering an
# .env the developer has added their own variables to.
[private]
env-check:
    [ -f .env ] || echo "UID=$(id -u)" > .env

# Run the webapp locally, via containers (--build keeps images in sync with the Containerfile).
dev: env-check
    {{compose}} up --build

alias compose := dev

# Build all containers locally.
build: env-check
    {{compose}} build

# The static checks below run with `--no-deps`: their tooling is baked into the
# dev images, so they need neither postgres, selenium, the webpack watcher nor
# the chart pregenerator. That keeps them usable without `just dev` running,
# locally and in CI alike.

# Check Python lint and formatting with ruff, without writing changes.
ruff: env-check
    # TODO: move `ruff` execution to host context; it shouldn't be running in the container
    {{compose}} run --rm -T --no-deps django bash -c "ruff check && ruff format --check"

# Apply ruff's fixes and formatting in place.
ruff-fix: env-check
    {{compose}} run --rm -T --no-deps django bash -c "ruff check --fix && ruff format"

# Static security analysis with bandit.
bandit: env-check
    {{compose}} run --rm -T --no-deps django ./scripts/bandit

# --skip-checks: Django's system checks import tracker.urls, and
# incident/api/views.py builds its OpenAPI parameters from the database at
# import time. Skipping them keeps this stack-free; `just test` still runs
# the full check framework. The consistent-history warning is expected.

# Fail if a model changed without a matching migration.
check-migrations: env-check
    {{compose}} run --rm -T --no-deps django bash -c "./manage.py makemigrations --dry-run --check --skip-checks"

# Jest, eslint and stylelint read sources directly rather than webpack's output,
# so no build is needed -- but node_modules lives in the bind-mounted tree,
# populated by the `node` service, so install it if absent. The guard is
# deliberately host-side, and skipping the install when the tree is already
# populated keeps a running `just dev` watcher undisturbed.
[private]
node-modules: env-check
    [ -d node_modules ] || {{compose}} run --rm --no-deps node npm ci

# Lint JavaScript with eslint.
eslint: node-modules
    {{compose}} run --rm --no-deps node npm run js-lint

# Lint SASS with stylelint.
stylelint: node-modules
    {{compose}} run --rm --no-deps node npm run stylelint

# Run all project linters.
lint: ruff bandit check-migrations eslint stylelint

# Run the Django test suite with coverage (CI enforces 100% on changed lines via diff-cover).
test:
    {{compose}} exec django bash -ec "\
        coverage run ./manage.py test --noinput; \
        coverage html; \
        coverage xml; \
        coverage report"

# The pregenerator image carries its own node_modules and bind-mounts only
# src/ and client/, so it needs no guard and no stack either.

# Run the jest suites for the frontend and the chart pregenerator.
test-js: node-modules
    {{compose}} run --rm --no-deps node npm test
    {{compose}} run --rm --no-deps node-chart-pregenerator npm run test

# Inject development data into the postgresql database.
createdevdata:
    {{compose}} exec django bash -c "./manage.py createdevdata"

# Import a postgres export file located at ./import.db.
import-db:
    {{compose}} exec -T postgresql bash -c "sed 's/OWNER TO [a-z]*/OWNER TO tracker/g' /django/import.db | psql trackerdb -U tracker > /dev/null"

# Save a snapshot of the database for the current git branch.
save-db:
    COMPOSE="{{compose}}" ./ci/scripts/savedb.sh

# Restore the most recent database snapshot for the current git branch.
restore-db:
    COMPOSE="{{compose}}" ./ci/scripts/restoredb.sh

# Open a browser pointed at the running dev site.
open-browser:
    COMPOSE="{{compose}}" ./ci/scripts/browser-open.sh

alias browser := open-browser

# Recompile prod + ci + dev lockfiles (forward flags, e.g. --upgrade or --upgrade-package=NAME).
pip-compile *FLAGS: (_pip-lock "requirements.txt" "requirements.in" FLAGS) (_pip-lock "ci-requirements.txt" "ci-requirements.in" FLAGS) (_pip-lock "dev-requirements.txt" "dev-requirements.in" FLAGS)

# Recompile only the dev lockfile (same flags as pip-compile).
pip-compile-dev *FLAGS: (_pip-lock "dev-requirements.txt" "dev-requirements.in" FLAGS)

# Recompile one lockfile in a clean builder matching the app's Python, so
# hashes resolve identically to production.
# The final chown hands the regenerated lockfile back to whoever owns the input;
# the builder runs as root, so without it a developer is left with root-owned
# requirements files in their checkout.
_pip-lock outfile infile *FLAGS:
    {{engine}} run --rm -v "{{justfile_directory()}}:/code:z" -w /code {{python_builder}} \
        bash -c 'apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && \
            pip install pip-tools=={{pip_tools_version}} && \
            pip-compile --generate-hashes --no-header --allow-unsafe {{FLAGS}} \
                --output-file {{outfile}} {{infile}} && \
            chown "$(stat -c "%u:%g" {{infile}})" {{outfile}}'

# Fail if the lockfiles are out of sync with the .in files.
pip-check: pip-compile
    git diff --exit-code -- requirements.txt ci-requirements.txt dev-requirements.txt

# Clean out local developer assets.
clean:
    rm -rvf ./node_modules

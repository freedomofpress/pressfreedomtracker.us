# Recipes for developing and testing the pressfreedomtracker.us website.
# Run `just` (or `just --list`) to see everything available.
#
# Container engine: prefers docker for backwards compat.
# Override explicitly with `CONTAINER_ENGINE=podman just <recipe>`.

engine := env_var_or_default("CONTAINER_ENGINE", "docker")
compose := engine + " compose"
# Locally built from the Containerfile's `poetry` stage, which holds both pins the
# resolver needs -- the app's interpreter and Poetry itself -- so there is no
# second copy to keep in step.
lock_image := "localhost/pressfreedomtracker-us-poetry-lock"
# Poetry's own hash-pinned requirements, rendered from the lock's `bootstrap` group.
bootstrap_reqs := "ci/containers/bootstrap-requirements.txt"

# Directory of hand-authored PNGs safe for automated optimization.
png_paths := "common/static/logos"
# Directory of hand-authored SVGs safe for automated optimization. Excludes
# common/templates/common (Django template tags embedded in <svg> attributes).
svg_paths := "client/common/icons"
# A binary in the bind-mounted node_modules, put there by the `node-modules`
# recipe rather than baked into the image.
svgo := "node_modules/.bin/svgo"
# Prefix for compose: git facts go in as env and build-args, since neither the
# build context nor a worktree's bind-mount carries a usable .git. Hex and base64
# values hold no whitespace, so the unquoted expansion splits cleanly.
git_facts := 'args="$(./ci/scripts/version-file.sh --build-args)" && env $args'
e2e_compose := compose + " --file=prod-docker-compose.yaml --file=e2e/compose.e2e.yaml"
# The playwright service sits behind the `e2e` profile, to keep it out of
# `qa-up`. Naming it on the command line is enough for docker compose, but
# podman-compose only honours a profile enabled with `--profile`, hence the
# flag on the `qa` recipe's `run` invocations below.
playwright := "/django/node_modules/.bin/playwright"
# Deployed environments targeted for QA testing are subdomains
qa_domain := "pressfreedomtracker.us"

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


# node_modules lives in the bind-mounted tree, populated by the `node` service's
# runtime `npm install` -- so a one-shot `compose run` finds it already there,
# unless nothing has populated it yet. The guard is deliberately host-side, and
# skipping the install when the tree is already populated keeps a running
# `just dev` watcher undisturbed.
[private]
node-modules: env-check
    [ -d node_modules ] || {{compose}} run --rm --no-deps node npm ci

# Run the webapp locally, via containers (--build keeps images in sync with the Containerfile).
dev: env-check
    {{git_facts}} {{compose}} up --build

alias compose := dev

# Build all containers locally.
build: env-check
    {{compose}} build

# Build the production image locally.
build-prod: env-check
    {{git_facts}} {{compose}} --file=prod-docker-compose.yaml build

# Run the webapp prod-like (gunicorn, DEBUG off), via containers; `dev`'s analog.
prod: build-prod
    {{compose}} --file=prod-docker-compose.yaml up

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

# Fail if a PNG under png_paths could be optimized further by oxipng.
pnglint: env-check
    {{compose}} run --rm -T --no-deps django \
        oxipng -r -o 6 --strip safe {{png_paths}}
    git diff --exit-code -- {{png_paths}}

# Fail if an SVG under svg_paths could be optimized further by svgo.
svglint: node-modules
    {{compose}} run --rm -T --no-deps node \
        {{svgo}} --config=svgo.config.mjs -r {{svg_paths}}
    git diff --exit-code -- {{svg_paths}}

# Lint JavaScript with eslint.
eslint: node-modules
    {{compose}} run --rm --no-deps node npm run js-lint

# Lint SASS with stylelint.
stylelint: node-modules
    {{compose}} run --rm --no-deps node npm run stylelint

# Run all project linters.
lint: ruff bandit check-migrations eslint stylelint pnglint svglint

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

# Run the QA stack with test data (then `just qa` in another terminal).
[doc('Run the QA stack locally with deterministic QA data')]
qa-up: env-check
    {{git_facts}} {{e2e_compose}} up --build

# ENV defaults to `local` (`just qa-up`) which runs in the same container
# CI uses so visual baselines are comparable.
# Any other name is a deployed environment at https://ENV.{{qa_domain}}.
# Any flags are forwarded to `playwright test`, e.g. `--grep=@smoke`
[doc('Run the browser test suite (`just qa [ENV] [FLAGS]`)')]
qa ENV="local" *FLAGS: env-check
    #!/usr/bin/env bash
    set -euo pipefail
    env='{{ENV}}'
    flags='{{FLAGS}}'
    # Pass off something that looks flag-like in the ENV parameter as a flag.
    case "$env" in -*|*/*|*.ts) flags="$env $flags"; env=local ;; esac

    # Run against the local QA stack. Guard that on a running stack, at least.
    # `exec` is the portable liveness probe: podman-compose's `ps` takes no
    # --status filter and lists stopped containers besides.
    if [ "$env" = local ]; then
        if ! {{e2e_compose}} exec -T django true >/dev/null 2>&1; then
            echo "just qa: no QA stack running -- start one with \`just qa-up\`" >&2
            exit 2
        fi
        # Naming the service enables its profile under docker compose, but
        # podman-compose honours a profile only when --profile asks for it.
        {{e2e_compose}} --profile=e2e run --rm --build --no-deps playwright {{playwright}} test $flags
        exit
    fi

    # Run against {{ENV}}.{{qa_domain}} with stored auth session data belonging
    # to the {{ENV}} (if it exists). Paths are relative to the repo, which is
    # the container's working directory too.
    storage=
    if [ -f "e2e/.auth/$env.json" ]; then storage="e2e/.auth/$env.json"; fi
    {{e2e_compose}} --profile=e2e run --rm --build --no-deps \
        --env E2E_ENV="$env" \
        --env E2E_BASE_URL="https://$env.{{qa_domain}}" \
        --env E2E_STORAGE_STATE="$storage" \
        playwright {{playwright}} test $flags

[doc('Record new visual baselines (`just qa-update [ENV] [FLAGS]`)')]
qa-update ENV="local" *FLAGS: (qa ENV "--update-snapshots " + FLAGS)

# Every ENV can have its own stored authentication (in e2e/.auth/ENV.json,
# captured with qa-auth), and baseline images for visual tests.
[doc('Capture a login session for `just qa ENV`')]
qa-auth ENV:
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p e2e/.auth
    state="e2e/.auth/{{ENV}}.json"

    url="https://{{ENV}}.{{qa_domain}}/admin/"

    # Start from an old session so anything still valid will continue to work
    if [ -f "$state" ]; then
        npx playwright open --load-storage="$state" --save-storage="$state" "$url"
    else
        npx playwright open --save-storage="$state" "$url"
    fi

# Inject development data into the postgresql database.
createdevdata:
    {{compose}} exec django bash -c "./manage.py createdevdata"

# Wipe the postgresql container and re-seed a fresh database via createdevdata.
reset-db: env-check && createdevdata
    {{compose}} rm -f postgresql
    {{git_facts}} {{compose}} up --build --wait

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

# Attach to the running Django container's console, e.g. for ipdb.
attach:
    {{engine}} attach $({{compose}} ps -q django)

# Re-resolve pyproject.toml into poetry.lock (forward flags, e.g. --regenerate).
lock *FLAGS: (_poetry "lock" FLAGS)

# Raise locked versions within pyproject's constraints (all of them, if unnamed).
lock-upgrade *PACKAGES: (_poetry "update" "--lock" PACKAGES)

# Runs Poetry, then always re-renders Poetry's own pins from poetry.lock.
# Arguments pass via the environment, and -f disables globbing, so shell
# metacharacters stay inert. The image runs as root; chown hands the output back
# to the checkout's owner.
_poetry +ARGS: lock-image
    {{engine}} run --rm -v "{{justfile_directory()}}:/code:z" -w /code \
        -e LOCK_ARGS={{quote(ARGS)}} {{lock_image}} \
        bash -efc 'poetry $LOCK_ARGS && \
            poetry export --only=bootstrap --output={{bootstrap_reqs}} && \
            sed -i "1i # Generated from poetry.lock by just lock -- do not edit." {{bootstrap_reqs}} && \
            chown "$(stat -c "%u:%g" justfile)" poetry.lock {{bootstrap_reqs}}'

[private]
lock-image:
    {{engine}} build --quiet --target=poetry --file=ci/containers/Containerfile --tag={{lock_image}} .

# Images install the checked-in lock, so no ordinary build notices drift.
# `check --lock` verifies the lock's pyproject hash without rewriting it; the
# re-render plus diff catches stale bootstrap pins.

# Fail if the generated files are out of sync with pyproject.toml.
lock-check: (_poetry "check" "--lock")
    git diff --exit-code --stat -- poetry.lock {{bootstrap_reqs}} >&2 \
        || { echo 'stale: run `just lock` and commit' >&2; exit 1; }

# Clean out local developer assets.
clean:
    rm -rvf ./node_modules

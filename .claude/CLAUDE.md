# U.S. Press Freedom Tracker

## Project Overview
- Django/Wagtail CMS website tracking press freedom incidents in the United States
- Python backend, Node.js/Webpack frontend asset bundling
- Separate Node.js chart pregenerator microservice
- Docker-based development environment

## Key Paths
- Django project settings: `tracker/settings/` (base, dev, production, production-ci)
- Django apps: `incident/`, `blog/`, `common/`, `statistics/`, `charts/`, `home/`, `forms/`, `emails/`, `menus/`, `dashboard/`, `geonames/`, `cloudflare/`, `styleguide/`, `build/`
- Frontend source: `client/` (common/js, charts/js, statistics/js)
- Chart pregenerator service: `chart_pregenerator/`
- Templates: each app has its own `templates/` directory
- Compiled bundles output: `build/static/bundles/`
- DevOps/Docker: `devops/docker/`, `devops/scripts/`
- Requirements: `requirements.txt`, `dev-requirements.txt`, `ci-requirements.txt` (compiled from `.in` files via pip-compile)

## Tech Stack
- Python 3.14, Django 5.2+, Wagtail 6.3+
- PostgreSQL 14
- Django REST Framework + drf-spectacular (OpenAPI docs)
- Webpack 5, Babel, React 18, D3 v7, Jest 29 (frontend)
- ESLint (airbnb config), Stylelint (sass-guidelines)
- Ruff (primary linter)
- Bandit (security)
- structlog for logging

## Development
- `make dev-init` for initial setup (creates `.env` with UID)
- `docker compose up` to start services (postgresql, django, node, node-chart-pregenerator, selenium)
- `docker compose exec django ./manage.py createdevdata` to seed dev data
- Web app at `http://localhost:8000`
- Wagtail admin at `/admin` (dev credentials: `test` / `test`)
- API docs at `/api/schema/swagger-ui/`
- Main branch: `develop`
- **All Django/Python commands must run inside Docker** via `docker compose exec django ...` (e.g., `docker compose exec django python manage.py makemigrations`). The host machine does not have Django or project dependencies installed.

## Testing
- Django tests: `make dev-tests` (runs with coverage via `coverage run ./manage.py test --noinput --failfast`)
- Jest tests: `make dev-jest-tests` (runs both main frontend and chart pregenerator tests)
- Migration check: `make check-migrations`
- CI enforces **100% coverage on changed lines** using `diff-cover` against `origin/develop`
- Tests use a custom `SeededDiscoveryRunner` with fixed seed (`876394101`) for reproducibility
- Tests live in `tests/` subdirectories within each Django app (e.g., `incident/tests/`)

## Linting and Code Quality
- `make ruff` — linter/formatter
- `make bandit` — security static analysis
- `make eslint` — JavaScript linting (airbnb config)
- `make stylelint` — SCSS linting (sass-guidelines config)
- Ruff configured in `pyproject.toml`: `select = ["I", "F4"]` (isort + unused imports), target py312, Django/Wagtail-aware import section ordering

## Dependency Management
- Uses pip-tools (`pip-compile`) for reproducible, hash-verified pinning
- Edit `.in` files, then `make compile-pip-dependencies` to recompile
- `make pip-update PACKAGE=name` to upgrade a specific package
- pip-compile runs inside a Docker container matching the production Python version

## Frontend Build System
- Webpack entries in `webpack.config.js`: `common`, `statistics`, `draftail`, `charts`, `filterSidebar`, `filterSummary`, `searchBar`, `verticalBarChart`, `treeMapChart`, `bubbleMapChart`, `hexbinMapChart`
- Output: `build/static/bundles/`
- `npm run start` = dev watch mode, `npm run build` = production build
- Module alias `~` maps to `client/common/js/` (both webpack and Jest)
- SCSS compiled via sass-loader + postcss-loader with Autoprefixer
- `webpack-bundle-tracker` writes `webpack-stats.json` for Django integration via `django-webpack-loader`

## Database
- Dev credentials: user `tracker`, password `trackerpassword`, db `trackerdb`, port `5432`
- `make dev-import-db` — import a database dump (place as `import.db` in repo root)
- `make dev-save-db` / `make dev-restore-db` — save/restore DB snapshots per branch

## Debugging
- `import ipdb; ipdb.set_trace()` in code, then `docker attach $(docker compose ps -q django)` to interact
- Detach without stopping: `Ctrl+P` then `Ctrl+Q`
- Profiling (when enabled in `tracker/settings/local.py`): `?prof` (cProfile), `?profile` (pyinstrument), `/silk` (Silk UI)

## Git Branching
- Development branch: `develop`
- Production branch: `prod`
- Feature branches fork from `develop`, PRs target `develop`

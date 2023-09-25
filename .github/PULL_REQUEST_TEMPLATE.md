## Description

Fixes #.

Changes proposed in this pull request:

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Vulnerabilities update
- [ ] Config changes
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] This change requires an admin update after deploy
- [ ] Includes a database migration removing  or renaming a field


## Testing

How should the reviewer test this PR?
Write out any special testing steps here.

### Post-deployment actions

In case this PR needs any admin changes or run a management command after deployment, mention it here:

## Checklist

### General checks

- [ ] Linting and tests pass locally
- [ ] The website and the changes are functional in Tor Browser
- [ ] There is no conflicting migrations
- [ ] Any CSP related changes required has been updated (check at least both firefox & chrome)
- [ ] The changes are accessible using keyboard and screenreader

### If you made changes to API flow:

- [ ] Verify that API responses are correct
- [ ] Verify that visualizations using the API endpoints are functional

### If you made changes to incident model metadata

- [ ] Verify incident export works correctly
- [ ] Verify incident filters are rendered correctly
- [ ] Verify incident filters show correct incidents
- [ ] Verify categories work
- [ ] Verify incidents are discoverable by search

### If you made changes to blog

- [ ] Verify that the blog index page renders correctly
- [ ] Verify that the individual blogs show all the informations correctly

### If you made changes to shared templates (e.g. card design, lead media, etc.)

- [ ] Verify that it renders correctly in homepage, if applicable
- [ ] Verify that it renders correctly in incident index page, if applicable
- [ ] Verify that it renders correctly in individual incident page, if applicable
- [ ] Verify that it renders correctly in blog index page, if applicable
- [ ] Verify that it renders correctly in individual blog page, if applicable

### If you made changes to email signup flow

- [ ] Verify that the email signup form in the footer renders and works
- [ ] Verify that the individual email signup pages work

### If you made changes to "Submit an Incident" form

- [ ] Verify that the form renders correctly and submit correctly as well

### If it's a major change

- [ ] Do the changes need to be tested in a separate staging instance?

### If you made any frontend change

If the PR involves some visual changes in the frontend, it is recommended to add a screenshot of the new visual.

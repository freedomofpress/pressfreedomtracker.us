# How to Contribute to the Press Freedom Tracker

The Press Freedom Tracker invites help from people able to contribute code, bug reports, and feature ideas.

## Reporting bugs, problems, or unexpected behavior

If you encounter something that is broken, confusing, or that you think could be improved, you should open a [GitHub Issue](https://github.com/freedomofpress/pressfreedomtracker.us/issues/new).  It's helpful to describe the situation in as much detail as you can, but you don't have to know why an error is occurring, or even if one is at all.

## New ideas and features

Do you have an idea for something new that you think belongs in the Press Freedom Tracker?  We are happy to hear about it.  Please [open an issue](https://github.com/freedomofpress/pressfreedomtracker.us/issues/new) describing your idea or feature, and the community and maintainers will give you feedback about it.

## Submitting code and patches

The Press Freedom Tracker follows the standard
[fork and pull](https://help.github.com/articles/using-pull-requests/)
model for code contributions via GitHub pull requests.

### Finding something to work on

If you're looking for an issue to work out, check out our [open issues](https://github.com/freedomofpress/pressfreedomtracker.us/issues) and look for ones tagged as [help wanted](https://github.com/freedomofpress/pressfreedomtracker.us/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22) or [small](https://github.com/freedomofpress/pressfreedomtracker.us/issues?q=is%3Aopen+is%3Aissue+label%3ASmall). These issues are the easiest way to start contributing, but if there are other items that catch your interest, please feel free to work on them.

### Let us know you're working on something

If there is a GitHub issue for the task you're working on, or if you've found one you'd like to start, please leave a comment to let people know that you are working on it.  This will prevent contributors from duplicating their efforts.

### Running the site locally

To get started working with the code, clone the repo and follow the instructions in the [README](README.rst).  If something in the instructions is not clear, or isn't working for you, you may open an issue describing your problem, or submit a pull request to improve the documentation.

### Code guidelines

* Python code should follow [PEP8](https://www.python.org/dev/peps/pep-0008) where possible.  One exception to this is line lengths beyond 79 characters are allowed.  You can check your compliance with the `make flake8` command.
* Writing tests is strongly encouraged, especially if significant behavior is added or changed.
  - Django-based tests are found in the `tests/` subdirectories of each separate app.  Run the entire test suite with `make dev-tests`
  - Javascript, jest-based tests are found in the `client/common/js/tests/` directory.  Run this test suite with `make dev-jest-tests`
* Javascript, CSS/Sass, and HTML markup should mimic the styles and patterns in the existing codebase.

## Conduct and communication

Please read the [Code of Conduct](https://github.com/freedomofpress/.github/blob/main/CODE_OF_CONDUCT.md) which people are expected to follow when discussing the Press Freedom Tracker on this GitHub repository, or other related venues.

# Contribution getting started

Contributions are highly welcomed and appreciated. Every little help
counts, so do not hesitate\! If you like pyrandall, also share some love on
Twitter or in your blog posts.

## Feature requests and feedback

We'd love to hear about your propositions and suggestions.
Feel free to [submit them as issues](https://github.com/kpn/pyrandall/issues)
and:

  - Explain what behaviour you would expect.
  - Keep the scope as narrow as possible. This will make it easier to
    implement.

## Report bugs

Report bugs for pyrandall in the [issue tracker](https://github.com/kpn/pyrandall/issues).

If you are reporting a bug, please include:

  - Your operating system name and version.
  - Any details about your local setup that might be helpful in
    troubleshooting, specifically the Python interpreter version,
    installed libraries, and pyrandall version.
  - Detailed steps to reproduce the bug, or - even better, a n xfaling
    test reproduces the bug

If you can write a demonstration test that currently fails but should
pass (xfail), that is a very useful commit to make as well, even if you
cannot fix the bug itself

## Fix bugs

Look through the GitHub issues for bugs. Here is a filter you can use:
<https://github.com/kpn/pyrandall/labels/bug:normal>

Don't forget to check the issue trackers of your favourite plugins,
too\!

## Implement features

Look through the GitHub issues for enhancements. Here is a filter you
can use: <https://github.com/kpn/pyrandall/labels/feature:new>

# Write documentation

pyrandall could always use more documentation. What exactly is needed?

  - More complementary documentation. Have you perhaps found something
    unclear?
  - Docstrings. There can never be too many of them.
  - Blog posts, articles and such -- they're all very appreciated.

You can also edit documentation files directly in the GitHub web
interface, without using a local copy. This can be convenient for small
fixes.

# Preparing Pull Requests


1.  [Fork the repository](https://help.github.com/articles/fork-a-repo/). :trident:

2.  Make your changes.

3.  open a [pull request](https://help.github.com/articles/about-pull-requests/)
    targeting the `master` branch.

4.  Follow **PEP-8**. There's a `tox` command to help fixing it: `tox -e
    fix-lint`. You can also add a pre commit hook to your local clone to
    run the style checks and fixes (see hint after running `tox -e
    fix-lint`)

5.  Tests for pyrandall are run using `tox`:

    `tox -e py36,fix-lint`

    NOTE:

    Requests in the tests are originally made to `stubserver.py` and cached with [VCR](https://vcrpy.readthedocs.io/en/latest/usage.html).
    Start the server in a virtualenv with `python stubserver.py`
    if you need to change / add test cases http requests. There are considerations to migrating to `pytest-httpserver`.
    Feedback or improvements are very welcomed :wink:


6.  Optionally check the docker build:

    `docker build -t pyrandall:local .

    smoke tests can be performed with `examples/pyrandall`

For a more detailed version please read [tox/CONTRIBUTING.rst](https://github.com/tox-dev/tox/blob/master/CONTRIBUTING.rst#long-version).


# Conventions

*Versioning*

See [semver](https://semver.org/). Find the package version in `./pyrandall/__init__.py` and `docker/VERSION` for the container.

*Please keep a changelog*

Please an entry for each version change in `CHANGELOG.md`. Follow the examples from [https://keepachangelog.com/](https://keepachangelog.com/)

*Git Commits*

First, use them often, they are free. Second; be descriptive.

An example:

```
The first line: short but sweet (max ~ 70 characters)

The second is intentionally left blank
More text can be added, format it how you want (max ~ 80 characters per line)
Don't use a full stop / period in your subject please

* Write in present tense
* motivate a change, why you changed X
```

Reference material
* https://www.conventionalcommits.org/en/v1.0.0-beta.2/
* https://chris.beams.io/posts/git-commit/

Commits should represent a savepoint of working code. Please do not write if this code works or not...


# Thank you

* We are thankful to you for spending your time on this project in any form.
* And a big thank you to the python community: `pytest` for being an inspiration. Maybe pyrandall will ever become just a pytest plugin.
* [tox](https://tox.readthedocs.io/en/latest/) project for writing a comprehensive CONTRIBUTING file!

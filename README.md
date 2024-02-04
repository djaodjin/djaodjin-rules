DjaoDjin-Rules
==============

[![PyPI version](https://badge.fury.io/py/djaodjin-rules.svg)](https://badge.fury.io/py/djaodjin-rules)

Flexible framework to check permissions to URIs and forward HTTP requests

This project contains bare bone templates. To see it in action, integrated into
a full-fledged subscription-based session proxy with bootstrap-styled
dashboards, take a look at [djaoapp](https://github.com/djaodjin/djaoapp/).

Development
===========

After cloning the repository, create a virtualenv environment and install
the prerequisites:

    $ python -m venv .venv
    $ source .venv/bin/activate
    $ pip install -r testsite/requirements.txt

It remains to create the database and populate it with test data.

    $ python ./manage.py migrate --run-syncdb --noinput
    $ python ./manage.py loaddata testsite/fixtures/test_data.json

Run the testsite

    $ python ./manage.py runserver


Release Notes
=============

Tested with

- **Python:** 3.7, **Django:** 3.2 ([LTS](https://www.djangoproject.com/download/))
- **Python:** 3.10, **Django:** 4.2 (latest)
- **Python:** 2.7, **Django:** 1.11 (legacy) - use testsite/requirements-legacy.txt

0.4.4

  * raises an error when trying to create a path with invalid characters
  * supports OpenAPI 3 schemas

[previous release notes](changelog)

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

- **Python:** 3.10, **Django:** 4.2 ([LTS](https://www.djangoproject.com/download/))
- **Python:** 3.12, **Django:** 5.1 (next)
- **Python:** 3.7, **Django:** 3.2 (legacy)

0.4.9

  * uses settings.AUTHENTICATION_OVERRIDE instead of as an App field
  * fixes `get_raw_uri` was removed in Django4.2

[previous release notes](changelog)

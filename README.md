Flexible framework to check permissions to URIs and forward HTTP requests

Tested with

- **Python:** 3.6, **Django:** 2.2 ([LTS](https://www.djangoproject.com/download/)), **Django Rest Framework:** 3.12
- **Python:** 3.6, **Django:** 3.2 (latest), **Django Rest Framework:** 3.12
- **Python:** 2.7, **Django:** 1.11 (legacy), **Django Rest Framework:** 3.9.4

This project contains bare bone templates. To see it in action, integrated into
a full-fledged subscription-based session proxy with bootstrap-styled
dashboards, take a look at [djaoapp](https://github.com/djaodjin/djaoapp/).

Development
===========

After cloning the repository, create a virtualenv environment and install
the prerequisites:

    $ virtualenv _installTop_
    $ source _installTop_/bin/activate
    $ pip install -r testsite/requirements.txt

It remains to create the database and populate it with test data.

    $ python ./manage.py migrate --run-syncdb --noinput
    $ python ./manage.py loaddata testsite/fixtures/test_data.json

Release Notes
=============

0.2.7

  * moves all language translations server-side
  * returns a URL as a string in all cases for `redirect_or_denied`

[previous release notes](changelog)

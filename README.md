Flexible framework to check permissions to URIs and forward HTTP requests

Tested with

- **Python:** 2.7, **Django:** 1.11, **Django Rest Framework:** 3.9.4
- **Python:** 3.6, **Django:** 2.2 ([LTS](https://www.djangoproject.com/download/)), **Django Rest Framework:** 3.10
- **Python:** 3.6, **Django:** 3.0 (latest), **Django Rest Framework:** 3.10

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

0.2.5

  * changes PUT to POST to generate new key
  * extends Vue with configuration constants
  * introduces compatibility with Django3

[previous release notes](changelog)

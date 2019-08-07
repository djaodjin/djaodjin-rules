Flexible framework to check permissions to URIs and forward HTTP requests

Tested with

- **Python:** 2.7, **Django:** 1.11.23 ([LTS](https://www.djangoproject.com/download/)), **Django Rest Framework:** 3.8.2
- **Python:** 3.6, **Django:** 1.11.23 ([LTS](https://www.djangoproject.com/download/)), **Django Rest Framework:** 3.8.2
- **Python:** 3.6, **Django:** 2.2.4 (latest),       **Django Rest Framework:** 3.8.2

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

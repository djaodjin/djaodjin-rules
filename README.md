flexible framework to check permissions to URIs and forward HTTP requests

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

Getting started
===============

Installation and configuration
------------------------------

First download and install the latest version of djaodjin-rules into a Python
virtual environment.

.. code-block:: shell

    $ pip install djaodjin-rules


Edit your project urls.py to add the djaojdin-rules urls

.. code-block:: python

   urlpatterns += [
       url(r'^', include('rules.urls')),
   ]


Edit your project settings.py to add rules into the ``INSTALLED_APPS``
and a RULES configuration block

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'rules'
    )

    RULES = {
    }

Various :doc:`configuration settings<settings>` are available.

The latest versions of django-restframework implement paginators disconnected
from parameters in  views (i.e. no more paginate_by). You will thus need
to define ``PAGE_SIZE`` in your settings.py

.. code-block:: python

    REST_FRAMEWORK = {
        'PAGE_SIZE': 25,
    }


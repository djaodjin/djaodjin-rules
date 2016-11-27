Custom rules
============

``RULE_OPERATORS`` is a list of functions that can be used to decorate
URLs.

Each function should return ``False`` if the proxy should forward
the request to the underlying view. A function could also return a string
that represents a redirect URL that will be inserted in the authorization
pipeline.

The first line of the ``__doc__`` string for a rule function is used
to describe it in the ``AppDashboardView`` drop-down select.


Example:

.. code-block:: python

    def fail_authenticated(request):
        """
        Authenticated
        """
        if not request.user.is_authenticated():
            return reverse(settings.LOGIN_URL)
        return False


A rule function can also define parameters whose arguments are either
instantiated by value in the URL under consideration or predefined
from an object in the database.


Example:

.. code-block:: python

    def fail_direct(request, organization=None, roledescription=None):
        """
        Direct %(saas.RoleDescription)s for :organization
        """
        if organization and not isinstance(organization, Organization):
            organization = get_object_or_404(Organization, slug=organization)
        return not(organization and _has_valid_access(
            request, [organization], roledescription=roledescription))


In the previous example, ``roledescription`` will defaults from values
in the database, while ``organization`` is taken out of the URL under
consideration.

If the model contains an ``account`` field and optionally an ``is_active``
field, the database objects will be filtered by it.

In case the following two objects are available in the database, two
rules will be available for the previous example in the ``AppDashboardView``
drop-down select.

.. code-block:: python

    {
      "fields": {
        "slug": "manager",
        "title": "Managers"
      },
      "model": "saas.RoleDescription", "pk": 1
    },
    {
      "fields": {
        "slug": "contributor",
        "title": "Contributors"
      },
      "model": "saas.RoleDescription", "pk": 2
    }

    # Available rules
    Direct Managers for :organization
    Direct Contributors for :organization


Using our Python API
====================

A minimal and full pythonic API for wedoist.com's web api.

Arguments:

    auth: An WedoistAuth object or a subclass that provides the required
          method.
          
    domain: The URI of the API.
    
    request_handler: A WedoistRequest class or subclass that provides 
          the required methods.

Examples:
---------

.. code-block:: python

    # Import the wedoist api
    from wedoistapi import Wedoist, WedoistHTTPAuth
    
    # Authenticate with the HTTP auth class.
    auth = WedoistHTTPAuth(email="foo@bar.com", password="bar")
    
    # Create an instance of the wedoist api using the user we authed to.
    wedoist = Wedoist(auth)
    
    # You can access the user's imformation in the auth objects 
    # user_data property
    default_project = auth.get_user_data()["default_project"]
    
    # To make an api call we use the names from the official api docs.
    # To access all of the active items on our users default project at
    # wedoist.com/API/Items/getAllActive we make the following call with 
    # the required POST data as keyword arguments:
    wedoist.Items.getAllActive(project_id=default_project)

Will return all active items as a list of python dictionaries, one for each item we fetched.

.. code-block:: json

    { "date_format": 0, 
      "default_project": 42, 
      "has_to_setup": 0, 
      "partition": 1, 
      "number_of_projects": 1, 
      "email": "foo@bar.com", 
      "time_format": 0, 
      "join_date": "Sun, 13 May 2012 20:20:53", 
      "avatar": "254bd140e8520bb8e25b5d2da98244b2", 
      "full_name": "John Cardholder", 
      "timezone": "America\/Chicago", 
      "id": 23
    }

Any API function call be called as presented in the official API
documentation with the required POST data passed as keyword 
arguments.

.. code-block:: python

    # API call: wedoist.com/API/Projects/getAll
    wedoist.Projects.getAll()
    
    # API call: wedoist.com/API/Projects/get
    wedoist.Projects.get(project_id=42)

Error Handling:
---------------

See WedoistRequest for more information.
    
For furthere information on the API specifics feel free to browse
the documentation at: <insert doc url here>

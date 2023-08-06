WedoistAPI
==========

A minimal and full pythonic API for wedoist.com's web api.

Arguments:

    auth: An WedoistAuth object or a subclass that provides the required
          method.
          
    domain: The URI of the API.
    
    request_handler: A WedoistRequest class or subclass that provides 
          the required methods.

Examples:

    >>> from wedoistapi import Wedoist, WedoistHTTPAuth
    
    # Authenticate with the HTTP auth class.
    >>> auth = WedoistHTTPAuth(email="foo@bar.com", password="bar")

    # Create an instance of the wedoist api using the user we authed to.
    >>> wedoist = Wedoist(auth)

    # You can access the user's imformation in the auth objects 
    # user_data property
    >>> default_project = auth.get_user_data()["default_project"]

    # To make an api call we use the names from the official api docs.
    # To access all of the active items on our users default project at
    # wedoist.com/API/Items/getAllActive we make the following call with 
    # the required POST data as keyword arguments:
    >>> wedoist.Items.getAllActive(project_id=default_project)

    # Will return all active items as a list of python dictionaries, one
    # for each item we fetched.
    
    { "91435": 
        [ { "date_due": null, 
            "comment_seen": 0, 
            "order": 1, 
            "content": "@Everyone This task", 
            "comment_count": 0, 
            "added_by": 42745, 
            "list_id": 91435, 
            "is_unread": false, 
            "project_id": 44146, 
            "id": 539934, 
            "date_due_string": "", 
            "posted":"Tue, 22 May 2012 21:10:14"
        } ] 
    }

Any API function call be called as presented in the official API
documentation with the required POST data passed as keyword 
arguments.

    # API call: wedoist.com/API/Projects/getAll
    >>> wedoist.Projects.getAll()

    # API call: wedoist.com/API/Projects/get
    >>> wedoist.Projects.get(project_id=42)

Error Handling:
    See WedoistRequest for more information.
    
    For furthere information on the API specifics feel free to browse
    the documentation at: <insert doc url here>
    


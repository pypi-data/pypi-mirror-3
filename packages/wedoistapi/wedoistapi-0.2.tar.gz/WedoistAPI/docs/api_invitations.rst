Invitations
-----------

getInviteSuggestions
~~~~~~~~~~~~~~~~~~~~

**Description:** 

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The id of the project to to get invite suggestions from.
    
    Example Value: "42" 

**Example Request:** ::

    http://wedoist.com/API/Invitations/getInviteSuggestions?project_id=42

.. code-block:: json
    
   
redeemInvite
~~~~~~~~~~~~

**Description:** 

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*password*
    The password.
    
    Example Value: "strong_password" 
*invite*
    The the invite code that was sent to the user though email.
    
    Example Value: "strong_password" 

**Example Request:** ::

    http://wedoist.com/API/Invitations/getInviteSuggestions?password=strong_password&invite=strong_password

.. code-block:: json
    
   {"date_format": 0, 
    "default_project": 42, 
    "has_to_setup": 0, 
    "partition": 1, 
    "number_of_projects": 1, 
    "email": "foo@bar.com", 
    "time_format": 0, 
    "join_date": "Fri, 25 May 2012 01:06:59", 
    "avatar": null, 
    "full_name": "John Wedoist", 
    "timezone": "US\/Arizona", 
    "id": 43670
    }
   
addUser
~~~~~~~

**Description:** Add either an existing user or invite a new user to join the project by email.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The id of the project to add the user too.
    
    Example Value: "42" 
*email*
    A valid email address of a current Wedoist user or to invite someone by email.
    
    Example Value: "foo@bar.com" 
*full_name (optional)*
    The name of the user to invite for email invitation.
    
    Example Value: "John Wedoist" 
*personal_note*
    A snippet of text to include in the email invitation.
    
    Example Value: "We need you on this John." 

**Example Request:** ::

    http://wedoist.com/API/Invitations/addUser?project_id=42&email=foo@bar.com&full_name=John Wedoist&personal_note=We need you on this John.

.. code-block:: json
    
   {'status': 'ADDED USER TO PROJECT.}
   



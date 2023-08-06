Users
-----

getTimezones
~~~~~~~~~~~~

**Description:** Returns a list of the timezones that the API allows.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*none*
    None
    
    Example Value: "None" 

**Example Request:** ::

    http://wedoist.com/API/Users/getTimezones?none=None

.. code-block:: json
    
   [ ['-1100', 'Pacific/Midway', '(GMT-1100) International Date Line West'],
      ['-1100', 'Pacific/Midway', '(GMT-1100) Midway Island'] ]
register
~~~~~~~~

**Description:** Register a new user on wedoist.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*email*
    A valid email address for the new user.
    
    Example Value: "foo@bar.com" 
*full_name*
    The new user's full name.
    
    Example Value: "John Wedoist" 
*password*
    The new user's password. It must contain 5 characters or more to be valid.
    
    Example Value: "strong_password" 
*timezone*
    The new user's timezone.
    
    Example Value: "Pacific/Midway" 

**Example Request:** ::

    http://wedoist.com/API/Users/register?email=foo@bar.com&full_name=John Wedoist&password=strong_password&timezone=Pacific/Midway

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
update
~~~~~~

**Description:** Update the logged in users account information.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*current_password*
    The current password of the user trying to update their information.
    
    Example Value: "strong_password" 
*email (optional)*
    The user's new email address to change to.
    
    Example Value: "foo@bar.com" 
*full_name (optional)*
    The user's new name.
    
    Example Value: "John Wedoist" 
*password (optional)*
    The user's new password. The password must be over 5 character to be valid.
    
    Example Value: "strong_password" 
*timezone (optional)*
    The user's new timezone.
    
    Example Value: "Pacific/Midway" 

**Example Request:** ::

    http://wedoist.com/API/?current_password=strong_password&email=foo@bar.com&full_name=John Wedoist&password=strong_password&timezone=Pacific/Midway

.. code-block:: json
    
   {"status": "ok"}
uploadPhoto
~~~~~~~~~~~

**Description:** Upload a photo for the user avatar with HTTP Post

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*image*
    The image data to upload.
    
    Example Value: "<file data>" 

**Example Request:** ::

    http://wedoist.com/API/Users/uploadPhoto?image=<file data>

.. code-block:: json
    
   {"status": "ok"}
getUser
~~~~~~~

**Description:** Get a single user from a project.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*project_id*
    The id of the project to get the user from
    
    Example Value: "42" 
*user_id*
    The id of the user to fetch.
    
    Example Value: "23" 

**Example Request:** ::

    http://wedoist.com/API/Users/getUser?project_id=42&user_id=23

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
logout
~~~~~~

**Description:** Log the user out of the service.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*none*
    None
    
    Example Value: "None" 

**Example Request:** ::

    http://wedoist.com/API/Users/logout?none=None

.. code-block:: json
    
   {"status": "ok"}
login
~~~~~

**Description:** Logs the user into Wedoist and returns the users details.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*email*
    A valid email for the registered user.
    
    Example Value: "foo@bar.com" 

**Example Request:** ::

    http://wedoist.com/API/Users/login?email=foo@bar.com

.. code-block:: json
        
   {"date_format": 0, 
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



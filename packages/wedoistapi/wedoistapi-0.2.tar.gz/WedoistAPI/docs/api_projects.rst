Projects
--------

unarchive
~~~~~~~~~

**Description:** Unarchive a project.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The id of the project to ubarchive.
    
    Example Value: "42" 

**Example Request:** ::

    http://wedoist.com/API/Projects/unarchive?project_id=42

.. code-block:: json
    
   {"status": "ok"}
   
getUsers
~~~~~~~~

**Description:** 

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*project_id*
    The id of the project to get the users from.
    
    Example Value: "42" 
*without_logged_in*
    Exclude the users that are logged in.
    
    Example Value: "false" 

**Example Request:** ::

    http://wedoist.com/API/Projects/getUsers?project_id=42&without_logged_in=false

.. code-block:: json
       
   [{"date_format": 0, 
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
    }, ]
get
~~~

**Description:** Get a project by it's id.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*project_id*
    The id of the project to fetch.
    
    Example Value: "42" 

**Example Request:** ::

    http://wedoist.com/API/Projects/get?project_id=42

.. code-block:: json
    
   { "archived": false, 
     "from_plan_unlimited": false, 
     "general_collection": 82, 
     "plan": "free", 
     "logo": null, 
     "privilege": "holder", 
     "inbox_list": 462, 
     "holder_uid": 314, 
     "id": 42, 
     "name": "Foo Project"} 
   
updateUserPrivilege
~~~~~~~~~~~~~~~~~~~

**Description:** 

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The id of the project to change the user's privilege in.
    
    Example Value: "32" 
*user_id*
    The id of the user to change the privilege on.
    
    Example Value: "462" 
*privilege*
    The intended privilege to assign to the user. Can be "user" or "holder"
    
    Example Value: "user" 

**Example Request:** ::

    http://wedoist.com/API/Projects/updateUserPrivilege?project_id=32&user_id=462&privilege=user

.. code-block:: json
    
   {"status": "ok"}
   
updateLastLogin
~~~~~~~~~~~~~~~

**Description:** Update the last time the user logged in to a particular project.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The id of the project to update the last logged in time on.
    
    Example Value: "34" 

**Example Request:** ::

    http://wedoist.com/API/?project_id=34

.. code-block:: json
    
   {"status": "ok"}
   
getAll
~~~~~~

**Description:** Returns all of the users projects. Optionally can filter for only active projects.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*only_active (optional)*
    Return only the active projects.
    
    Example Value: "false" 

**Example Request:** ::

    http://wedoist.com/API/Projects/getAll?only_active=false

.. code-block:: json
    
   { "archived": false, 
     "from_plan_unlimited": false, 
     "general_collection": 82, 
     "plan": "free", 
     "logo": null, 
     "privilege": "holder", 
     "inbox_list": 462, 
     "holder_uid": 314, 
     "id": 42, 
     "name": "Foo Project"} 
   
add
~~~

**Description:** Create a new project.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*name*
    The name of the new project.
    
    Example Value: "Foo Project Redux" 

**Example Request:** ::

    http://wedoist.com/API/Projects/add?name=Foo Project Redux

.. code-block:: json
    
   { "archived": false, 
     "from_plan_unlimited": false, 
     "general_collection": 82, 
     "plan": "free", 
     "logo": null, 
     "privilege": "holder", 
     "inbox_list": 462, 
     "holder_uid": 314, 
     "id": 42, 
     "name": "Foo Project"} 
   
removeUser
~~~~~~~~~~

**Description:** Remove a user from a project.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The id of the project to remove the user from.
    
    Example Value: "42" 
*user_id*
    The id of the user to remove.
    
    Example Value: "462" 

**Example Request:** ::

    http://wedoist.com/API/Projects/removeUser?project_id=42&user_id=462

.. code-block:: json
    
   {"status": "ok"}
   
deleteProjectLogo
~~~~~~~~~~~~~~~~~

**Description:** Delete the logo from a project.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The id of the project to delete the logo from.
    
    Example Value: "42" 

**Example Request:** ::

    http://wedoist.com/API/?project_id=42

.. code-block:: json
    
   {"status": "ok"}
   
getWithData
~~~~~~~~~~~

**Description:** Get a list of project with it's data.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*project_id*
    The id of the project to fetch.
    
    Example Value: "42" 
*update_last_login (optional)*
    Update the last login?
    
    Example Value: "false" 
*only_active (optional)*
    Return only active projects.
    
    Example Value: "false" 

**Example Request:** ::

    http://wedoist.com/API/getWithData?project_id=42&update_last_login=false&only_active=false

.. code-block:: json
    
   [{ "archived": false, 
     "from_plan_unlimited": false, 
     "general_collection": 82, 
     "plan": "free", 
     "logo": null, 
     "privilege": "holder", 
     "inbox_list": 462, 
     "holder_uid": 314, 
     "id": 42, 
     "name": "Foo Project"}, ]
   
archive
~~~~~~~

**Description:** Archive a project.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The id of the project to archive.
    
    Example Value: "42" 

**Example Request:** ::

    http://wedoist.com/API/Projects/archive?project_id=42

.. code-block:: json
    
   {"status": "ok"}
   
uploadProjectLogo
~~~~~~~~~~~~~~~~~

**Description:** Upload a project logo with an HTTP POST request.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The id of the project to upload the logo too.
    
    Example Value: "42" 
*image*
    The image data.
    
    Example Value: "<file data>" 

**Example Request:** ::

    http://wedoist.com/API/Projects/uploadProjectLogo?project_id=42&image=<file data>

.. code-block:: json
    
   {"status": "ok"}
   
delete
~~~~~~

**Description:** Delete a project.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The id of the project to delete.
    
    Example Value: "42" 
*current_password (optional)*
    The user's current password.
    
    Example Value: "strong_password" 

**Example Request:** ::

    http://wedoist.com/API/Projects/delete?project_id=42&current_password=strong_password

.. code-block:: json
    
   { "archived": false, 
     "from_plan_unlimited": false, 
     "general_collection": 82, 
     "plan": "free", 
     "logo": null, 
     "privilege": "holder", 
     "inbox_list": 462, 
     "holder_uid": 314, 
     "id": 42, 
     "name": "Foo Project"} 
   



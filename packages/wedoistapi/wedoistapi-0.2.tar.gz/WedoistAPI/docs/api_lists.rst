Lists
-----

unarchive
~~~~~~~~~

**Description:** Unarchive an archived list.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*id*
    The id of the list to unarchive.
    
    Example Value: "23" 

**Example Request:** ::

    http://wedoist.com/API/?id=23

.. code-block:: json
    
   { "archived": false, 
     "project_id": 42, 
     "order": 504, 
     "name": "Foo Man Choo", 
     "id": 23} 
   
move
~~~~

**Description:** Move a list to another project.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*id*
    The id of the list to move.
    
    Example Value: "23" 
*project_id*
    The id of the project to move the list to.
    
    Example Value: "43" 

**Example Request:** ::

    http://wedoist.com/API/?id=23&project_id=43

.. code-block:: json
    
   { "archived": false, 
     "project_id": 43, 
     "order": 504, 
     "name": "Foo Man Choo", 
     "id": 23} 
   
get
~~~

**Description:** Returns the details of a single list item by its id.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*id*
    The id of the project.
    
    Example Value: "23" 

**Example Request:** ::

    http://wedoist.com/API/Lists/get?id=23

.. code-block:: json
    
   {"archived": false, 
     "name": "Inbox", 
     "id": 23, 
     "is_inbox": true, 
     "project_id": 42, 
     "order": 0
    }
   
getAll
~~~~~~

**Description:** Returns the details of all ofthe lists associated with a project.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*project_id*
    The id of the tasklist.
    
    Example Value: "23" 

**Example Request:** ::

    http://wedoist.com/API/Lists/getAll?project_id=23

.. code-block:: json
    
   [
    {"archived": false, 
    "name": "Inbox", 
    "id": 23, 
    "is_inbox": true, 
    "project_id": 42, 
    "order": 0
    }, 
    
    {"archived": false, 
    "name": "Important List", 
    "id": 24, 
    "is_inbox": true, 
    "project_id": 42, 
    "order": 0
    }, ]
   
updateOrders
~~~~~~~~~~~~

**Description:** Updates how the lists are ordered.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*orders*
    A JSON list of the list's order.
    
    Example Value: "[3,4,1,2]" 

**Example Request:** ::

    http://wedoist.com/API/Lists/updateOrders?orders=[3,4,1,2]

.. code-block:: json
    
   {"status": "ok"}
   
update
~~~~~~

**Description:** Change the name or order of a list.   

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*id*
    The id of the list.
    
    Example Value: "23" 
*name (optional)*
    The new name for the list.
    
    Example Value: "Foo Man Choo" 
*order (optional)*
    The order of the list.
    
    Example Value: "3" 

**Example Request:** ::

    http://wedoist.com/API/Lists/update?id=23&name=Foo Man Choo&order=3

.. code-block:: json
    
    {"archived": false, 
     "project_id": 44146, 
     "order": 503, 
     "name": "Foo Man Choo", 
     "id": 93340
    }
   
archive
~~~~~~~

**Description:** Archive a list.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*id*
    The id of the list to archive.
    
    Example Value: "23" 

**Example Request:** ::

    http://wedoist.com/API/Lists/archive?id=23

.. code-block:: json
    
   { "archived": true, 
     "name": "Foo Man Choo", 
     "id": 23, 
     "archived_date": "Fri, 25 May 2012 19:28:24", 
     "project_id": 42, 
     "order": 503
    } 
   
add
~~~

**Description:** 

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The project to add the list to.
    
    Example Value: "42" 
*name*
    The name of the list.
    
    Example Value: "Foo List" 
*order*
    The order to place this list in the list of lists.
    
    Example Value: "2" 

**Example Request:** ::

    http://wedoist.com/API/Lists/add?project_id=42&name=Foo List&order=2

.. code-block:: json
    
   {"archived": false, 
     "project_id": 42, 
     "order": 3, 
     "name": "Foo List", 
     "id": 23
     } 
   
getArchived
~~~~~~~~~~~

**Description:** Get a list of the archived lists in a project.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*project_id*
    The id of the project to fetch the archived lists from.
    
    Example Value: "42" 
*offset*
    The first item in the list of archived lists.
    
    Example Value: "10" 
*limit*
    Limit the number of results to return.
    
    Example Value: "20" 

**Example Request:** ::

    http://wedoist.com/API/Lists/getArchived?project_id=42&offset=10&limit=20

.. code-block:: json
    
   [{"archived": true, 
     "project_id": 44146, 
     "order": 503, 
     "name": "Foo Man Choo", 
     "id": 93340
    },]
   
delete
~~~~~~

**Description:** Delete a task list

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*id*
    The id of the tasklist
    
    Example Value: "23" 

**Example Request:** ::

    http://wedoist.com/API/Lists/delete?id=23

.. code-block:: json
    
   {"archived": false, 
     "project_id": 42, 
     "order": 3, 
     "name": "Foo List", 
     "id": 23}
   



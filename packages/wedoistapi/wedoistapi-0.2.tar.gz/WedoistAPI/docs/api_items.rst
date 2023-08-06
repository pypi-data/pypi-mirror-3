Items
-----

complete
~~~~~~~~

**Description:** Mark an item as complete.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*item_id*
    The id of the item to mark complete.
    
    Example Value: "256" 

**Example Request:** ::

    http://wedoist.com/API/Items/complete?item_id=256

.. code-block:: json
    
   {"date_due": null, 
    "comment_seen": 0, 
    "order": 1, 
    "content": "Grow a beard.", 
    "comment_count": 0, 
    "added_by": 23, 
    "list_id": 93340, 
    "is_unread": false, 
    "project_id": 42, 
    "id": 256, 
    "date_due_string": "", 
    "posted": "Mon, 28 May 2012 17:36:03"}
   
get
~~~

**Description:** Get an item by its id.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*item_id*
    The id of the item to fetch.
    
    Example Value: "256" 

**Example Request:** ::

    http://wedoist.com/API/Items/get?item_id=256

.. code-block:: json
    
   {"date_due": null, 
    "comment_seen": 0, 
    "order": 1, 
    "content": "Grow a beard.", 
    "comment_count": 0, 
    "added_by": 23, 
    "list_id": 93340, 
    "is_unread": false, 
    "project_id": 42, 
    "id": 546631, 
    "date_due_string": "", 
    "posted": "Mon, 28 May 2012 17:36:03"}
   
uncomplete
~~~~~~~~~~

**Description:** Mark the item as uncomplete.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*item_id*
    The id of the item to mark uncomplete.
    
    Example Value: "256" 

**Example Request:** ::

    http://wedoist.com/API/Items/uncomplete?item_id=256

.. code-block:: json
    
   {"date_due": null, 
    "comment_seen": 0, 
    "order": 1, 
    "content": "Grow a beard.", 
    "comment_count": 0, 
    "added_by": 23, 
    "list_id": 93340, 
    "is_unread": false, 
    "project_id": 42, 
    "id": 256, 
    "date_due_string": "", 
    "posted": "Mon, 28 May 2012 17:36:03"}
   
updateOrders
~~~~~~~~~~~~

**Description:** Update the order of the items.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*orders*
    A JSON list of the item's order.
    
    Example Value: "[3,4,1,2]" 

**Example Request:** ::

    http://wedoist.com/API/Items/updateOrders?orders=[3,4,1,2]

.. code-block:: json
    
   {'status': 'ok'}
   
update
~~~~~~

**Description:** Update an item.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*item_id*
    The id of the item to update.
    
    Example Value: "256" 
*due_date_string (optional)*
    Set the date the item is due. Could be every day or every day @ 10.
    
    Example Value: ""every day"" 
*content (optional)*
    The content of the item.
    
    Example Value: "Finish TPS reports." 
*comment_seen (optional)*
    Filter by seen comments.
    
    Example Value: "false" 

**Example Request:** ::

    http://wedoist.com/API/Items/update?item_id=256&due_date_string="every day"&content=Finish TPS reports.&comment_seen=false

.. code-block:: json
    
   {"date_due": null, 
    "comment_seen": 0, 
    "order": 1, 
    "content": "Grow a beard.", 
    "comment_count": 0, 
    "added_by": 23, 
    "list_id": 93340, 
    "is_unread": false, 
    "project_id": 42, 
    "id": 256, 
    "date_due_string": "", 
    "posted": "Mon, 28 May 2012 17:36:03"}
   
getAllActive
~~~~~~~~~~~~

**Description:** 

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*project_id*
    The id of the project to fetch items from.
    
    Example Value: "42" 
*with_dates_only (optional)*
    Return only active with due dates?
    
    Example Value: "false" 
*by_list_id (optional)*
    The list id to limit the query by.
    
    Example Value: "23" 

**Example Request:** ::

    http://wedoist.com/API/Items/getAllActive?project_id=42&with_dates_only=false&by_list_id=23

.. code-block:: json
    
   {"93340": [{ "date_due": null, 
                "comment_seen": 0, 
                "order": 1, 
                "content": "Grow a beard.", 
                "comment_count": 0, 
                "added_by": 23, 
                "list_id": 93340, 
                "is_unread": false, 
                "project_id": 42, 
                "id": 256, 
                "date_due_string": "", 
                "posted": "Mon, 28 May 2012 17:36:03"},]
   }
   
add
~~~

**Description:** 

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*content*
    The content of the item.
    
    Example Value: "Finish TPS reports." 
*list_id*
    The id of the list to add the item to.
    
    Example Value: "256" 
*due_date_string (optional)*
    Set the date the item is due. Could be every day or every day @ 10.
    
    Example Value: "none" 
*order (optional)*
    The order of the item reltive to other items in this list.
    
    Example Value: "2" 
*ignore_date_error (optional)*
    Ignore errors with the date.
    
    Example Value: "false" 
*note (optional)*
    Add an optional note
    
    Example Value: "Simple note." 

**Example Request:** ::

    http://wedoist.com/API/Items/add?content=Finish TPS reports.&list_id=256&due_date_string=none&order=2&ignore_date_error=false&note=Simple note.

.. code-block:: json
    
   {"date_due": null, 
    "comment_seen": 0, 
    "order": 1, 
    "content": "Grow a beard.", 
    "comment_count": 0, 
    "added_by": 23, 
    "list_id": 93340, 
    "is_unread": false, 
    "project_id": 42, 
    "id": 256, 
    "date_due_string": "", 
    "posted": "Mon, 28 May 2012 17:36:03"}
   
getActive
~~~~~~~~~

**Description:** Get all active items from a list.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*list_id*
    The id of the list to get the items from.
    
    Example Value: "486" 

**Example Request:** ::

    http://wedoist.com/API/Items/getActive?list_id=486

.. code-block:: json
    
    [ { "date_due": null, 
        "comment_seen": 0, 
        "order": 1, 
        "content": "Grow a beard.", 
        "comment_count": 0, 
        "added_by": 23, 
        "list_id": 93340, 
        "is_unread": false, 
        "project_id": 42, 
        "id": 546631, 
        "date_due_string": "", 
        "posted": "Mon, 28 May 2012 17:36:03"
      },
   ]
   
   
query
~~~~~

**Description:** Query all of the projects items.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*project_id*
    The project to query.
    
    Example Value: "42" 
*queries*
    A JSON list of queries.
    
    Example Value: "TODO" 
*user_id (optional)*
    Filter by user_id.
    
    Example Value: "23" 
*as_count (optional)*
    Return only counts.
    
    Example Value: "false" 

**Example Request:** ::

    http://wedoist.com/API/Items/query?project_id=42&queries=TODO&user_id=23&as_count=false

.. code-block:: json
    
   {"date_due": null, 
    "comment_seen": 0, 
    "order": 1, 
    "content": "Grow a beard.", 
    "comment_count": 0, 
    "added_by": 23, 
    "list_id": 93340, 
    "is_unread": false, 
    "project_id": 42, 
    "id": 256, 
    "date_due_string": "", 
    "posted": "Mon, 28 May 2012 17:36:03"}
   
getCompleted
~~~~~~~~~~~~

**Description:** 

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*list_id*
    The list to fetch completed items from.
    
    Example Value: "256" 
*offset (optional)*
    The offset to the first returned item.
    
    Example Value: "10" 
*limit (optional)*
    The maximum number of items to return.
    
    Example Value: "30" 

**Example Request:** ::

    http://wedoist.com/API/Items/getCompleted?list_id=256&offset=10&limit=30

.. code-block:: json
    
   {"items": [{ "date_due": null, 
                "comment_seen": 0, 
                "order": 1, 
                "content": "Grow a beard.", 
                "comment_count": 0, 
                "added_by": 23, 
                "list_id": 93340, 
                "is_unread": false, 
                "project_id": 42, 
                "id": 256, 
                "date_due_string": "", 
                "posted": "Mon, 28 May 2012 17:36:03"}]}, 
    "users":[{"default_project": 42, 
              "has_to_setup": false, 
              "email": "foo@bar.com", 
              "number_of_projects": 2, 
              "join_date": "Sun, 13 May 2012 20:20:53", 
              "avatar": "254bd140e8520bb8e25b5d2da98244b2", 
              "full_name": "Frank Wedoist", 
              "promo.guided_tour": true, 
              "timezone": "America\/Chicago", 
              "id": 23}]
    }
   
delete
~~~~~~

**Description:** 

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*item_id*
    The id of the item to delete.
    
    Example Value: "256" 

**Example Request:** ::

    http://wedoist.com/API/Items/delete?item_id=256

.. code-block:: json
    
   {"date_due": null, 
    "comment_seen": 0, 
    "order": 1, 
    "content": "Grow a beard.", 
    "comment_count": 0, 
    "added_by": 23, 
    "list_id": 93340, 
    "is_unread": false, 
    "project_id": 42, 
    "id": 256, 
    "date_due_string": "", 
    "posted": "Mon, 28 May 2012 17:36:03"}
   



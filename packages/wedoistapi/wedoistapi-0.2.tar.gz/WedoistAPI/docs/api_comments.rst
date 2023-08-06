Comments
--------

get
~~~

**Description:** Fetch a comment by its id.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*comment_id*
    The id of the comment to be fetched.
    
    Example Value: "256" 

**Example Request:** ::

    http://wedoist.com/API/Comments/get?comment_id=256

.. code-block:: json
    
    { "content": "A simple comment.", 
      "user_id": 42745, 
      "type_id": "status", 
      "item_id": 967046, 
      "project_id": 44146, 
      "id": 368500, 
      "posted": "Sun, 27 May 2012 18:06:43"
    }
   
getUnread
~~~~~~~~~

**Description:** Get all unread comments from a project.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*project_id*
    The id of the target project.
    
    Example Value: "42" 
*as_count (optional)*
    Return a count of the comments for display without fetchign them all.
    
    Example Value: "true" 
*as_ids (optional)*
    Return the ids of the comments?
    
    Example Value: "false" 

**Example Request:** ::

    http://wedoist.com/API/Comments/getUnread?project_id=42&as_count=true&as_ids=false

.. code-block:: json
    
   { "content": "A simple comment.", 
      "user_id": 42745, 
      "type_id": "status", 
      "item_id": 967046, 
      "project_id": 44146, 
      "id": 368500, 
      "posted": "Sun, 27 May 2012 18:06:43"
    }
   
markAsRead
~~~~~~~~~~

**Description:** Mark comments as read.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The target project.
    
    Example Value: "42" 
*item_ids*
    The ids items to be marked as read.
    
    Example Value: "[256,276]" 

**Example Request:** ::

    http://wedoist.com/API/Comments/markAsRead?project_id=42&item_ids=[256,276]

.. code-block:: json
    
   {'status': 'ok'}
   
getAll
~~~~~~

**Description:** Get all of the comments associated with the item.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*type_id*
    The type of comment. Can be of type status, chat_log, item, or document
    
    Example Value: "item" 
*item_id*
    The id of the item.
    
    Example Value: "256" 
*update_comment_seen (optional)*
    Update the fetched comments as seen?
    
    Example Value: "false" 
*include_users (optional)*
    Include the users?
    
    Example Value: "false" 
*include_project_labels (optional)*
    Include the project labels?
    
    Example Value: "false" 

**Example Request:** ::

    http://wedoist.com/API/Comments/getAll?type_id=item&item_id=256&update_comment_seen=false&include_users=false&include_project_labels=false

.. code-block:: json
    
      { "project_id": 43, 
        "comment_seen": 1, 
        "comments": [{ "content": "A simple comment.", 
                       "user_id": 42745, 
                       "type_id": "status", 
                       "item_id": 967046, 
                       "project_id": 44146, 
                       "id": 368500, 
                       "posted": "Sun, 27 May 2012 18:06:43"
                    },]
   }  
   
update
~~~~~~

**Description:** Update a comments content.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*comment_id*
    The id of the comment to update.
    
    Example Value: "256" 
*content*
    The content to update the comment with.
    
    Example Value: "Sorry I mean SPT reports!" 

**Example Request:** ::

    http://wedoist.com/API/Comments/update?comment_id=256&content=Sorry I mean SPT reports!

.. code-block:: json
    
   { "content": "A simple comment.", 
      "user_id": 42745, 
      "type_id": "status", 
      "item_id": 967046, 
      "project_id": 44146, 
      "id": 368500, 
      "posted": "Sun, 27 May 2012 18:06:43"
    }
   
markAsUnread
~~~~~~~~~~~~

**Description:** Mark comments as unread.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The target project.
    
    Example Value: "42" 
*item_ids*
    The ids items to be marked as unread.
    
    Example Value: "[256,276]" 

**Example Request:** ::

    http://wedoist.com/API/Comments/markAsUnread?project_id=42&item_ids=[256,276]

.. code-block:: json
    
   {'status': 'ok'}
   
add
~~~

**Description:** Add a comment to an item.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The id of the target project.
    
    Example Value: "42" 
*type_id*
    The type of comment. Can be of type status, chat_log, item, or document
    
    Example Value: "item" 
*item_id*
    The item to attach the comment to.
    
    Example Value: "256" 
*content*
    The content of the comment.
    
    Example Value: "Those TPS reports look good Gordan." 
*mark_as_unread_for_others (optional)*
    Mark this as unread to the other users in the project?
    
    Example Value: "0" 
*notify_users_via_email*
    Should a notification be sent via email?
    
    Example Value: "true" 

**Example Request:** ::

    http://wedoist.com/API/Comments/add?project_id=42&type_id=item&item_id=256&content=Those TPS reports look good Gordan.&mark_as_unread_for_others=0&notify_users_via_email=true

.. code-block:: json
    
   { "content": "A simple comment.", 
      "user_id": 42745, 
      "type_id": "status", 
      "item_id": 967046, 
      "project_id": 44146, 
      "id": 368500, 
      "posted": "Sun, 27 May 2012 18:06:43"
    }
   
delete
~~~~~~

**Description:** Delete a comment.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*comment_id*
    The id of the comment to delete.
    
    Example Value: "256" 

**Example Request:** ::

    http://wedoist.com/API/Comments/delete?comment_id=256

.. code-block:: json
    
   { "content": "A simple comment.", 
      "user_id": 42745, 
      "type_id": "status", 
      "item_id": 967046, 
      "project_id": 44146, 
      "id": 368500, 
      "posted": "Sun, 27 May 2012 18:06:43"
    }
   



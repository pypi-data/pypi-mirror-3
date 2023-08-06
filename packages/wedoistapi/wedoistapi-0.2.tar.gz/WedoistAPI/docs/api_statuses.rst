Statuses
--------

get
~~~

**Description:** Get a single status by id.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*status_id*
    The id of the status to fetch.
    
    Example Value: "256" 
*content_rendering (optional)*
    Enable rendering of the content.
    
    Example Value: "false" 

**Example Request:** ::

    http://wedoist.com/API/Statuses/get?status_id=256&content_rendering=false

.. code-block:: json
    
    { "posted": "Mon, 28 May 2012 18:18:43", 
      "type_id": 1, 
      "comment_seen": 0, 
      "poster_uid": 23, 
      "content": "I grew my beard overnight!!", 
      "comment_count": 0, 
      "project_id": 42, 
      "id": 256, 
      "is_unread": false}
   
getAll
~~~~~~

**Description:** Get all statuses in a project.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*project_id*
    The if of the project to fetch the statuses from.
    
    Example Value: "42" 
*type_id (optional)*
    Can be of type status, chat_log, item, or document
    
    Example Value: "item" 
*poster_uid (optional)*
    Filter the statuses by user_id
    
    Example Value: "23" 
*offset_date (optional)*
    The date to offset the statuses by.
    
    Example Value: "2012-3-24T23:59" 
*offset_id (optional)*
    Offset to the first status returned.
    
    Example Value: "14" 
*limit (optional)*
    Limit the number of statuses returned.
    
    Example Value: "10" 
*content_rendering (optional)*
    Enable rendering of the content.
    
    Example Value: "false" 

**Example Request:** ::

    http://wedoist.com/API/Statuses/getAll?project_id=42&type_id=item&poster_uid=23&offset_date=2012-3-24T23:59&offset_id=14&limit=10&content_rendering=false

.. code-block:: json
    
   { "users": { "42745": {"default_project": 44146, 
                          "stats": {"status_updates": 1, 
                                    "completed_tasks": 5, 
                                    "comments": 2}, 
                          "has_to_setup": false, 
                          "email": "porketind00d@gmail.com",
                          "number_of_projects": 2, 
                          "join_date": "Sun, 13 May 2012 20:20:53",
                          "last_login": "Mon, 28 May 2012 18:18:27",
                          "avatar": "254bd140e8520bb8e25b5d2da98244b2",
                          "full_name": "apitest", 
                          "promo.guided_tour": true, 
                          "privilege": "holder", 
                          "timezone": "America\/Chicago", 
                          "id": 42}
               }, 
     "statuses": [{ "posted": "Mon, 28 May 2012 18:18:43", 
                    "type_id": 1, 
                    "comment_seen": 0, 
                    "poster_uid": 23, 
                    "content": "I grew my beard overnight!!", 
                    "comment_count": 0, 
                    "project_id": 42, 
                    "id": 256, 
                    "is_unread": false}]
                  }
      }
   
update
~~~~~~

**Description:** Update a status.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*status_id*
    The id of the status to update.
    
    Example Value: "256" 
*content*
    The content of the status.
    
    Example Value: "I grew my beard overnight!!" 

**Example Request:** ::

    http://wedoist.com/API/Statuses/update?status_id=256&content=I grew my beard overnight!!

.. code-block:: json
    
    { "posted": "Mon, 28 May 2012 18:18:43", 
      "type_id": 1, 
      "comment_seen": 0, 
      "poster_uid": 23, 
      "content": "I grew my beard overnight!!", 
      "comment_count": 0, 
      "project_id": 42, 
      "id": 256, 
      "is_unread": false}
   
getByDate
~~~~~~~~~

**Description:** Get a list of statuses by date.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*project_id*
    The if of the project to fetch the statuses from.
    
    Example Value: "42" 
*date*
    The date to filter by.
    
    Example Value: "2012-3-24T23:59" 
*content_rendering (optional)*
    Enable rendering of the content.
    
    Example Value: "false" 

**Example Request:** ::

    http://wedoist.com/API/Statuses/getByDate?project_id=42&date=2012-3-24T23:59&content_rendering=false

.. code-block:: json
    
   { "users": { "42745": {"default_project": 44146, 
                          "stats": {"status_updates": 1, 
                                    "completed_tasks": 5, 
                                    "comments": 2}, 
                          "has_to_setup": false, 
                          "email": "porketind00d@gmail.com",
                          "number_of_projects": 2, 
                          "join_date": "Sun, 13 May 2012 20:20:53",
                          "last_login": "Mon, 28 May 2012 18:18:27",
                          "avatar": "254bd140e8520bb8e25b5d2da98244b2",
                          "full_name": "apitest", 
                          "promo.guided_tour": true, 
                          "privilege": "holder", 
                          "timezone": "America\/Chicago", 
                          "id": 42}
               }, 
     "statuses": [{ "posted": "Mon, 28 May 2012 18:18:43", 
                    "type_id": 1, 
                    "comment_seen": 0, 
                    "poster_uid": 23, 
                    "content": "I grew my beard overnight!!", 
                    "comment_count": 0, 
                    "project_id": 42, 
                    "id": 256, 
                    "is_unread": false}]
                  }
      }
   
add
~~~

**Description:** Add a status to a project.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*project_id*
    The if of the project to add the status to.
    
    Example Value: "42" 
*content*
    The content of the status.
    
    Example Value: "I grew my beard overnight!!" 
*type_id (optional)*
    Can be of type status, chat_log, item, or document
    
    Example Value: "item" 

**Example Request:** ::

    http://wedoist.com/API/Statuses/add?project_id=42&content=I grew my beard overnight!!&type_id=item

.. code-block:: json
    
    { "posted": "Mon, 28 May 2012 18:18:43", 
      "type_id": 1, 
      "comment_seen": 0, 
      "poster_uid": 23, 
      "content": "I grew my beard overnight!!", 
      "comment_count": 0, 
      "project_id": 42, 
      "id": 256, 
      "is_unread": false}
   
delete
~~~~~~

**Description:** 

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*status_id*
    The id of the status to delete.
    
    Example Value: "256" 

**Example Request:** ::

    http://wedoist.com/API/Statuses/delete?status_id=256

.. code-block:: json
    
    { "posted": "Mon, 28 May 2012 18:18:43", 
      "type_id": 1, 
      "comment_seen": 0, 
      "poster_uid": 23, 
      "content": "I grew my beard overnight!!", 
      "comment_count": 0, 
      "project_id": 42, 
      "id": 256, 
      "is_unread": false}
   



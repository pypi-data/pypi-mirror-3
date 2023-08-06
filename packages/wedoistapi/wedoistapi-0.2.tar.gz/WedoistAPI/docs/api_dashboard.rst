Dashboard
---------

getAllPeople
~~~~~~~~~~~~

**Description:** Return all of the users in all of the projects.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*None*
    
    
    Example Value: "" 

**Example Request:** ::

    http://wedoist.com/API/Dashboard/getAllPeople?None=

.. code-block:: json
    
   { "23": { "default_project": 44146, 
                "has_to_setup": false, 
                "id": 23, 
                "number_of_projects": 2, 
                "join_date": "Sun, 13 May 2012 20:20:53", 
                "avatar": "254bd140e8520bb8e25b5d2da98244b2", 
                "full_name": "John Wedoist", 
                "promo.guided_tour": true, 
                "timezone": "America\/Chicago", 
                "email": "foo@bar.com"}
    }

   
getAllProjectUpdates
~~~~~~~~~~~~~~~~~~~~

**Description:** Get all updates from all projects.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*type_id(optional)*
    The type of updates to fetch. Can be of type status, chat_log, item, or document
    
    Example Value: "item" 
*poster_uid (optional)*
    Filter by user_id.
    
    Example Value: "23" 
*limit (optional)*
    Limit the number of results returned by the query.
    
    Example Value: "3" 
*only_active (optional)*
    Filter by active projects only.
    
    Example Value: "false" 

**Example Request:** ::

    http://wedoist.com/API/Dashboard/getAllProjectUpdates?type_id(optional)=item&poster_uid=23&limit=3&only_active=false

.. code-block:: json
    
    { "logged_in_user": { "default_project": 42, 
                          "stats": { "status_updates": 2, 
                                     "completed_tasks": 0, 
                                     "comments": 2 } 
                          "has_to_setup": false, 
                          "email": "foo@bar.com", 
                          "number_of_projects": 2, 
                          "join_date": "Sun, 13 May 2012 20:20:53", 
                          "last_login": "Mon, 28 May 2012 13:29:42", 
                          "avatar": "254bd140e8520bb8e25b5d2da98244b2", 
                          "full_name": "Frank Wedoist", 
                          "promo.guided_tour": true, 
                          "privilege": "holder", 
                          "timezone": "America\/Chicago", 
                          "id": 42745}, 
      "users": { "42745": { "default_project": 42, 
                            "stats": { "status_updates": 2, 
                                       "completed_tasks": 0, 
                                       "comments": 2}, 
                            "has_to_setup": false, 
                            "email": "foo@bar.com", 
                            "number_of_projects": 2, 
                            "join_date": "Sun, 13 May 2012 20:20:53", 
                            "last_login": "Mon, 28 May 2012 13:29:42", 
                            "avatar": "254bd140e8520bb8e25b5d2da98244b2", 
                            "full_name": "Frank Wedoist", 
                            "promo.guided_tour": true, 
                            "privilege": "holder", 
                            "timezone": "America\/Chicago", 
                            "id": 256 }
               }, 
      "project_data": [ {"project": { "archived": false, 
                                      "from_plan_unlimited": false, 
                                      "general_collection": 45935, 
                                      "plan": "free", 
                                      "logo": null, 
                                      "privilege": "holder", 
                                      "inbox_list": 91435, 
                                      "holder_uid": 42, 
                                      "id": 44146, 
                                      "name": "Foo Project"}, 
                         "statuses":[{"posted": "Sun, 27 May 2012 19:35:23",
                                      "type_id": 5, 
                                      "comment_seen": 0, 
                                      "poster_uid": 42, 
                                      "content": "Simple status update.", 
                                      "comment_count": 1},]
                          },
                        ]
       }
   
getAllUnreadStats
~~~~~~~~~~~~~~~~~

**Description:** Return the unread stats from all the projects.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*only_active (optional)*
    Filter by active projects only.
    
    Example Value: "false" 

**Example Request:** ::

    http://wedoist.com/API/Dashboard/getAllUnreadStats?only_active=false

.. code-block:: json
    
   [{"stats": [{"status_updates": 1, 
                "project_id": 42, 
                "completed_tasks": 0, 
                "comments": 0}, 
               {"status_updates": 2, 
                "project_id": 44146, 
                "completed_tasks": 0, 
                "comments": 2}], 
     "user": {"default_project": 42, 
              "has_to_setup": false, 
              "email": "foo@bar.com", 
              "number_of_projects": 2, 
              "join_date": "Sun, 13 May 2012 20:20:53", 
              "avatar": "254bd140e8520bb8e25b5d2da98244b2", 
              "full_name": "Frank Wedoist", 
              "promo.guided_tour": true, 
              "timezone": "America\/Chicago", 
              "id": 42745}
    },]
   
getAllUserStats
~~~~~~~~~~~~~~~

**Description:** Return the user stats from all of the projects.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*None*
    
    
    Example Value: "" 

**Example Request:** ::

    http://wedoist.com/API/Dashboard/getAllUserStats?None=

.. code-block:: json
    
   { "stats": [{"status_updates": 1, 
                "project_id": 42, 
                "completed_tasks": 0, 
                "comments": 0}, 
               {"status_updates": 2, 
                "project_id": 44146, 
                "completed_tasks": 0, 
                "comments": 2}], 
     "user": {"default_project": 42, 
              "has_to_setup": false, 
              "email": "foo@bar.com", 
              "number_of_projects": 2, 
              "join_date": "Sun, 13 May 2012 20:20:53", 
              "avatar": "254bd140e8520bb8e25b5d2da98244b2", 
              "full_name": "Frank Wedoist", 
              "promo.guided_tour": true, 
              "timezone": "America\/Chicago", 
              "id": 42745}
    }
   
getAllTasks
~~~~~~~~~~~

**Description:** Get all tasks from all projects.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*date (optional)*
    Filter the returned tasks by date.
    
    Example Value: "2012-3-24" 
*user_id (optional)*
    Filter the returned tasks by user_id
    
    Example Value: "23" 
*as_count (optional)*
    Return only counts of the tasks.
    
    Example Value: "false" 
*only_active (optional)*
    Filter by active tasks only.
    
    Example Value: "true" 

**Example Request:** ::

    http://wedoist.com/API/Dashboard/getAllTasks?date=2012-3-24&user_id=23&as_count=false&only_active=true

.. code-block:: json
    
   [{ "project": { "archived": false, 
                   "from_plan_unlimited": false, 
                   "general_collection": 46988, 
                   "plan": "free", 
                   "logo": null, 
                   "privilege": "holder", 
                   "inbox_list": 93315, 
                   "holder_uid": 42745, 
                   "id": 45120, 
                   "name": "another one"}, 
       "users": [{"default_project": 42, 
                  "has_to_setup": false, 
                  "email": "foo@bar.com", 
                  "number_of_projects": 2, 
                  "join_date": "Sun, 13 May 2012 20:20:53", 
                  "avatar": "254bd140e8520bb8e25b5d2da98244b2", 
                  "full_name": "Frank Wedoist", 
                  "promo.guided_tour": true, 
                  "timezone": "America\/Chicago", 
                  "id": 42745},],
   },]
                 
   



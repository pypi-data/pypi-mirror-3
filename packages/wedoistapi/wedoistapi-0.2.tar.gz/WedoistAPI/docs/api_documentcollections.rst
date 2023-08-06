DocumentCollections
-------------------

unarchive
~~~~~~~~~

**Description:** Unarchive a document collection.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*id*
    The id of the document collection to unarchive.
    
    Example Value: "23" 

**Example Request:** ::

    http://wedoist.com/API/DocumentCollections/unarchive?id=23

.. code-block:: json
    
   {"archived": false, 
    "documents": [ {"description": "", 
                    "title": "Simple google doc", 
                    "url": "https://docs.google.com/doc", 
                    "comment_seen": 0, 
                    "order": 2, 
                    "comment_count": 0, 
                    "date_created": "Sun, 27 May 2012 19:35:23",
                    "collection_id": 45935, 
                    "project_id": 44146, 
                    "id": 8856, 
                    "added_by": 42745, 
                    "is_unread": false}
                 ], 
    "name": "General", 
    "id": 45935, 
    "is_inbox": true, 
    "project_id": 44146, 
    "order": 0}
   
move
~~~~

**Description:** 

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*id*
    The id of the document collection to move.
    
    Example Value: "23" 
*to_project_id*
    The project to move the document collection to.
    
    Example Value: "42" 

**Example Request:** ::

    http://wedoist.com/API/DocumentCollections/move?id=23&to_project_id=42

.. code-block:: json
    
   {"archived": false, 
    "documents": [ {"description": "", 
                    "title": "Simple google doc", 
                    "url": "https://docs.google.com/doc", 
                    "comment_seen": 0, 
                    "order": 2, 
                    "comment_count": 0, 
                    "date_created": "Sun, 27 May 2012 19:35:23",
                    "collection_id": 45935, 
                    "project_id": 42, 
                    "id": 8856, 
                    "added_by": 42745, 
                    "is_unread": false}
                 ], 
    "name": "General", 
    "id": 45935, 
    "is_inbox": true, 
    "project_id": 44146, 
    "order": 0}
   
get
~~~

**Description:** Get a single document collection.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*id*
    The id of the document collection to fetch.
    
    Example Value: "23" 

**Example Request:** ::

    http://wedoist.com/API/DocumentCollections/get?id=23

.. code-block:: json
    
   {"archived": false, 
    "documents": [ {"description": "", 
                    "title": "Simple google doc", 
                    "url": "https://docs.google.com/doc", 
                    "comment_seen": 0, 
                    "order": 2, 
                    "comment_count": 0, 
                    "date_created": "Sun, 27 May 2012 19:35:23",
                    "collection_id": 45935, 
                    "project_id": 44146, 
                    "id": 8856, 
                    "added_by": 42745, 
                    "is_unread": false}
                 ], 
    "name": "General", 
    "id": 45935, 
    "is_inbox": true, 
    "project_id": 44146, 
    "order": 0}
   
getAll
~~~~~~

**Description:** Get all document collections in a project.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*project_id*
    The project id to fetch the document collections from.
    
    Example Value: "42" 

**Example Request:** ::

    http://wedoist.com/API/DocumentCollections/getAll?project_id=42

.. code-block:: json
    
   [ {"archived": false, 
      "documents": [ {"description": "", 
                      "title": "Simple google doc", 
                      "url": "https://docs.google.com/doc", 
                      "comment_seen": 0, 
                      "order": 2, 
                      "comment_count": 0, 
                      "date_created": "Sun, 27 May 2012 19:35:23",
                      "collection_id": 45935, 
                      "project_id": 44146, 
                      "id": 8856, 
                      "added_by": 42745, 
                      "is_unread": false}
                   ], 
      "name": "General", 
      "id": 45935, 
      "is_inbox": true, 
      "project_id": 44146, 
      "order": 0} ] 
   
updateOrders
~~~~~~~~~~~~

**Description:** Update the orders of the document collections.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The id of the target project.
    
    Example Value: "32" 
*orders*
    A JSON list of the document collections's order.
    
    Example Value: "[3,4,1,2]" 

**Example Request:** ::

    http://wedoist.com/API/DocumentCollections/updateOrders?project_id=32&orders=[3,4,1,2]

.. code-block:: json
    
   {"status": "ok"}
   
update
~~~~~~

**Description:** Update a document collection.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*id*
    The id of the target document collection.
    
    Example Value: "23" 
*name (optional)*
    A new name for the document collection.
    
    Example Value: "Old Foo Docs" 
*order*
    The order of this document collection.
    
    Example Value: "2" 

**Example Request:** ::

    http://wedoist.com/API/DocumentCollections/update?id=23&name=Old Foo Docs&order=2

.. code-block:: json
    
   {"archived": false, 
    "documents": [ {"description": "", 
                    "title": "Simple google doc", 
                    "url": "https://docs.google.com/doc", 
                    "comment_seen": 0, 
                    "order": 2, 
                    "comment_count": 0, 
                    "date_created": "Sun, 27 May 2012 19:35:23",
                    "collection_id": 45935, 
                    "project_id": 44146, 
                    "id": 8856, 
                    "added_by": 42745, 
                    "is_unread": false}
                 ], 
    "name": "General", 
    "id": 45935, 
    "is_inbox": true, 
    "project_id": 44146, 
    "order": 0}
   
archive
~~~~~~~

**Description:** Archive a document collection.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*id*
    The id of the document collection to archive.
    
    Example Value: "12" 

**Example Request:** ::

    http://wedoist.com/API/DocumentCollections/archive?id=12

.. code-block:: json
    
   {"archived": true, 
    "documents": [ {"description": "", 
                    "title": "Simple google doc", 
                    "url": "https://docs.google.com/doc", 
                    "comment_seen": 0, 
                    "order": 2, 
                    "comment_count": 0, 
                    "date_created": "Sun, 27 May 2012 19:35:23",
                    "collection_id": 45935, 
                    "project_id": 44146, 
                    "id": 8856, 
                    "added_by": 42745, 
                    "is_unread": false}
                 ], 
    "name": "General", 
    "id": 45935, 
    "is_inbox": true, 
    "project_id": 44146, 
    "order": 0}
   
getArchived
~~~~~~~~~~~

**Description:** Get all of the archived document collections from a project.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*project_id*
    The project to fetch the document collections from.
    
    Example Value: "42" 
*offset (optional)*
    The offset of the starting document collection.
    
    Example Value: "10" 
*limit (optional)*
    The maximum amount of archived document collections to return.
    
    Example Value: "30" 

**Example Request:** ::

    http://wedoist.com/API/DocumentCollections/getArchived?project_id=42&offset=10&limit=30

.. code-block:: json
    
   [ {"archived": false, 
      "documents": [ {"description": "", 
                      "title": "Simple google doc", 
                      "url": "https://docs.google.com/doc", 
                      "comment_seen": 0, 
                      "order": 2, 
                      "comment_count": 0, 
                      "date_created": "Sun, 27 May 2012 19:35:23",
                      "collection_id": 45935, 
                      "project_id": 44146, 
                      "id": 8856, 
                      "added_by": 42745, 
                      "is_unread": false}
                   ], 
      "name": "General", 
      "id": 45935, 
      "is_inbox": true, 
      "project_id": 44146, 
      "order": 0} ] 
   
delete
~~~~~~

**Description:** Delete a document collection.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*id*
    The id of the target document collection.
    
    Example Value: "23" 

**Example Request:** ::

    http://wedoist.com/API/DocumentCollections/delete?id=23

.. code-block:: json
    
   {"archived": false, 
    "documents": [ {"description": "", 
                    "title": "Simple google doc", 
                    "url": "https://docs.google.com/doc", 
                    "comment_seen": 0, 
                    "order": 2, 
                    "comment_count": 0, 
                    "date_created": "Sun, 27 May 2012 19:35:23",
                    "collection_id": 45935, 
                    "project_id": 44146, 
                    "id": 8856, 
                    "added_by": 42745, 
                    "is_unread": false}
                 ], 
    "name": "General", 
    "id": 45935, 
    "is_inbox": true, 
    "project_id": 44146, 
    "order": 0}
   



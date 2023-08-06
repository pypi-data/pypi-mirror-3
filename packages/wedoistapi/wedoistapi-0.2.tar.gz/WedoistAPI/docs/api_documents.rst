Documents
---------

get
~~~

**Description:** Get a document

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*id*
    The id of the document to fetch.
    
    Example Value: "257" 

**Example Request:** ::

    http://wedoist.com/API/Documents/get?id=257

.. code-block:: json
    
    {"description": "Simple description", 
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
   
lock
~~~~

**Description:** Lock a document.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*id*
    The id of the document to lock.
    
    Example Value: "345" 

**Example Request:** ::

    http://wedoist.com/API/Documents/lock?id=345

.. code-block:: json
    
   {"status": "ok"}
   
updateOrders
~~~~~~~~~~~~

**Description:** Updates the document's orders.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*orders*
    A JSON list of the document's order.
    
    Example Value: "[3,4,1,2]" 

**Example Request:** ::

    http://wedoist.com/API/Documents/updateOrders?orders=[3,4,1,2]

.. code-block:: json
    
   {"status": "ok"}
   
update
~~~~~~

**Description:** Update a document

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*id*
    The id of the document to update.
    
    Example Value: "345" 
*title*
    The title of the updated document
    
    Example Value: "TPS Reports" 
*url*
    The url of the updated document.
    
    Example Value: "http://foo.com/tps" 
*description (optional)*
    The description of the updated document.
    
    Example Value: " TPS reports." 
*order*
    The position of this document relative to others in this collection.
    
    Example Value: "2" 

**Example Request:** ::

    http://wedoist.com/API/Documents/update?id=345&title=TPS Reports&url=http://foo.com/tps&description= TPS reports.&order=2

.. code-block:: json
    
    {"description": "Simple description", 
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
   
add
~~~

**Description:** Add a document.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*collection_id*
    The collection to add the document to.
    
    Example Value: "256" 
*title*
    The title of the document
    
    Example Value: "TPS Reports" 
*url*
    The url of the document.
    
    Example Value: "http://foo.com/tps" 
*description (optional)*
    The description of the document.
    
    Example Value: "March TPS reports." 
*users_to_notify (optional)*
    A list of users to notify.
    
    Example Value: "[gary, sue, john]" 

**Example Request:** ::

    http://wedoist.com/API/Documents/add?collection_id=256&title=TPS Reports&url=http://foo.com/tps&description=March TPS reports.&users_to_notify=[gary, sue, john]

.. code-block:: json
    
    {"description": "Simple description", 
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
   
addAsNewVersion
~~~~~~~~~~~~~~~

**Description:** Add a new version of a document.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*document_to_replace*
    The id of the document to replace.
    
    Example Value: "345" 
*title*
    The title of the updated document
    
    Example Value: "TPS Reports" 
*url*
    The url of the updated document.
    
    Example Value: "http://foo.com/tps" 
*description (optional)*
    The description of the updated document.
    
    Example Value: "March TPS reports." 
*users_to_notify (optional)*
    A list of users to notify.
    
    Example Value: "[gary, sue, john]" 

**Example Request:** ::

    http://wedoist.com/API/Documents/addAsNewVersion?document_to_replace=345&title=TPS Reports&url=http://foo.com/tps&description=March TPS reports.&users_to_notify=[gary, sue, john]

.. code-block:: json
    
    {"description": "Simple description", 
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
   
unlock
~~~~~~

**Description:** Unlock a document.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*id*
    The id of the document to delete
    
    Example Value: "23" 

**Example Request:** ::

    http://wedoist.com/API/Documents/unlock?id=23

.. code-block:: json
    
   {"status": "ok"}
   
getCollectionDocuments
~~~~~~~~~~~~~~~~~~~~~~

**Description:** Get all of the documents in a collection.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*collection_id*
    The id of the collection the documents should be fetched from.
    
    Example Value: "23" 

**Example Request:** ::

    http://wedoist.com/API/Documents/getCollectionDocuments?collection_id=23

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
   
delete
~~~~~~

**Description:** 

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*id*
    The id of the document to delete.
    
    Example Value: "23" 

**Example Request:** ::

    http://wedoist.com/API/Documents/delete?id=23

.. code-block:: json
    
    {"description": "Simple description", 
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
   



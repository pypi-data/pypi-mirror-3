Chat
----

isPermanentOffline
~~~~~~~~~~~~~~~~~~

**Description:** Is the user marked permanently offline?

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The id of the target project to make the user as offonline.
    
    Example Value: "42" 

**Example Request:** ::

    http://wedoist.com/API/Chat/isPermanentOffline?project_id=42

.. code-block:: json
    
   {"result": false}
   
addMessage
~~~~~~~~~~

**Description:** 

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The id of the target project to add the chat message to.
    
    Example Value: "42" 

**Example Request:** ::

    http://wedoist.com/API/Chat/addMessage?project_id=42

.. code-block:: json
    
   {"status": "ok"}
   
markPermanentOffline
~~~~~~~~~~~~~~~~~~~~

**Description:** Mark the user as permanently offline in the specified project

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The project id of
    
    Example Value: "42" 

**Example Request:** ::

    http://wedoist.com/API/Chat/markPermanentOffline?project_id=42

.. code-block:: json
    
   {"status": "ok"}
   
getLatestMessages
~~~~~~~~~~~~~~~~~

**Description:** 

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The id of the target project to get the latest messages from.
    
    Example Value: "42" 

**Example Request:** ::

    http://wedoist.com/API/Chat/getLatestMessages?project_id=42

.. code-block:: json
    
    [{"timestamp": 1338140975.35, 
      "message": "This is a message.", 
      "posted": "Sun, 27 May 2012 17:49:35", 
      "id": "7e9c6d5925f9ac356018c2f0e8eabc3d", 
      "from_uid": 54
     },] 

   
markOnlineBroadcast
~~~~~~~~~~~~~~~~~~~

**Description:** 

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The id of the target project to make the user as online.
    
    Example Value: "42" 

**Example Request:** ::

    http://wedoist.com/API/Chat/markOnlineBroadcast?project_id=42

.. code-block:: json
    
   [54]
   
markOnlinePoll
~~~~~~~~~~~~~~

**Description:** Poll the server updating your online status and return a list of online users.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*project_id*
    The project id of target project.
    
    Example Value: "42" 

**Example Request:** ::

    http://wedoist.com/API/Chat/markOnlinePoll?project_id=42

.. code-block:: json
    
   [54]
   



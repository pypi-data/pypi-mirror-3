Labels
------

add
~~~

**Description:** Add a new label to the project.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*project_id*
    The id of the project to add the label to.
    
    Example Value: "42" 
*label*
    The label to add.
    
    Example Value: "asap!" 

**Example Request:** ::

    http://wedoist.com/API/Labels/add?project_id=42&label=asap!

.. code-block:: json
    
   { "people_label": true, 
     "user_id": 42, 
     "name": "Frank Wedoist"}
   
getAll
~~~~~~

**Description:** Get all the labels from a project.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*project_id*
    The id of the project to fetch the labels from.
    
    Example Value: "42" 

**Example Request:** ::

    http://wedoist.com/API/Labels/getAll?project_id=42

.. code-block:: json
    
   [{ "people_label": false, 
      "name": "Everyone"}, 
    { "people_label": true, 
      "user_id": 42, 
      "name": "Frank Wedoist"}]
   
delete
~~~~~~

**Description:** Delete a label from the project.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*project_id*
    The id of the project to delete the label from.
    
    Example Value: "42" 
*label*
    The label to delete.
    
    Example Value: "asap!" 

**Example Request:** ::

    http://wedoist.com/API/Labels/delete?project_id=42&label=asap!

.. code-block:: json
    
   { "people_label": true, 
     "user_id": 42, 
     "name": "Frank Wedoist"}
   



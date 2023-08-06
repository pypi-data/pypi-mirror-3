Search
------

search
~~~~~~

**Description:** Search a project.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*project_id*
    The id of the project to search.
    
    Example Value: "42" 
*query*
    A JSON list of the queries.
    
    Example Value: "TODO I dont know exactly what to do here." 
*limit*
    Limit the number of returned results.
    
    Example Value: "10" 
*offset*
    The offset to the first returned result.
    
    Example Value: "30" 
*filter_by*
    Can be of type status, chat_log, item, or document
    
    Example Value: "item" 
*sort_by*
    How to sort the returned search items.
    
    Example Value: "relevancy" 

**Example Request:** ::

    http://wedoist.com/API/Search/search?project_id=42&query=TODO I dont know exactly what to do here.&limit=10&offset=30&filter_by=item&sort_by=relevancy

.. code-block:: json
    
   TODO: Json example of search.
   



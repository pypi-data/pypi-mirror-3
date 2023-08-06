Trends
------

getTrendGraph
~~~~~~~~~~~~~

**Description:** 

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*project_id*
    The id of the project to fetch the graph form.
    
    Example Value: "42" 
*user_id (optional)*
    Limit the graph to a single user_id.
    
    Example Value: "23" 
*width (optional)*
    The width of the graph.
    
    Example Value: "350" 
*height (optional)*
    The height of the graph.
    
    Example Value: "200" 
*days (optional)*
    How many days to show in the graph.
    
    Example Value: "7" 

**Example Request:** ::

    http://wedoist.com/API/Trends/getTrendGraph?project_id=42&user_id=23&width=350&height=200&days=7

.. code-block:: json
    
   "http://chart.apis.google.com/chart?cht=...
   



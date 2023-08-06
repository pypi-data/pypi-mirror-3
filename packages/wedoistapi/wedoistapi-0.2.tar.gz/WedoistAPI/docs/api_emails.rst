Emails
------

add
~~~

**Description:** Add an email.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*email*
    The email to add. Must be a valid email.
    
    Example Value: "Foo@bar.com" 

**Example Request:** ::

    http://wedoist.com/API/Emails/add?email=Foo@bar.com

.. code-block:: json
    
   {'status': 'ok'}
   
getAll
~~~~~~

**Description:** Get all emails.

**Response Format:** JSON

**HTTP Method:** GET

**Parameters:**

    
*None*
    
    
    Example Value: "" 

**Example Request:** ::

    http://wedoist.com/API/Emails/getAll?None=

.. code-block:: json
    
   
remove
~~~~~~

**Description:** Remove an email.

**Response Format:** JSON

**HTTP Method:** POST

**Parameters:**

    
*email*
    The email to remove. Must be a valid email.
    
    Example Value: "Foo@bar.com" 

**Example Request:** ::

    http://wedoist.com/API/Emails/remove?email=Foo@bar.com

.. code-block:: json
    
   {'status': 'ok'}
   



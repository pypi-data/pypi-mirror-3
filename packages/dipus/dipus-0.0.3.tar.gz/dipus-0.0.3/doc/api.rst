API
============

.. note:: API is under development. will be change frequently.

Dipus server API is under the REST interface.


This API is inspired from `elastic search <http://www.elasticsearch.org/guide/reference/api/>`_

register document
-------------------------

::

 curl -XPOST 'http://localhost:9200/spam/' -d '{
    "_index" : "spam",
    "title": "Here comes new document!"
    "path" : "dir/test1",
    "message" : "Some thing new document"
}'


Return

::

{
    "ok" : true,
    "_index" : "spam",
    "_id" : "1"
}

Delete document
--------------------


::

  curl -XDELETE 'http://localhost:9200/spam/1'

::

{
    "ok" : true,
    "_index" : "spam",
    "_id" : "1",
    "found" : true
}

Get document itself
-------------------------

*Not implemented yet*

::

  curl -XGET 'http://localhost:9200/spam/1'

::

{
    "_index" : "spam",
    "_id" : "1", 
    "_source" : {
        "postDate" : "2012-08-25T14:12:12",
        "message" : "Some thing new document"
    }
}


search
---------


::

  curl -XGET 'http://localhost:9200/spam/_search?q=Test'
    or 
  curl -XGET 'http://localhost:9200/spam/_search?q=Test?callback=jsonp10293'

::

{
    "hits":{
        "total" : 1,
        "hits" : [
            {
                "_index" : "spam",
                "_id" : "1", 
                "_source" : {
                    "postDate" : "2012-08-25T14:12:12",
                    "title": "Here comes new document!",
                    "path": "dir/test1",
                    "message" : "Some thing new document"
                }
            }
        ]
    }
}


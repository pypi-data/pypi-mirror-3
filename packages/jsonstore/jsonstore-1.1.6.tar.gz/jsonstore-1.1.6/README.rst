Jsonstore
=========

*A simple database for the web*

Part I. Python API
------------------

This is a draft documentation for a small project of mine called JSONStore. JSONStore is a schema-free database for JSON documents, exposed using a REST API; it has much in common with CouchDB, although it's much simpler and doesn't intend to be a complete database. Instead, it focus on document searching using a simple matching algorithm that I invented.

JSONStore uses SQLite for indexing, and can be installed using EasyInstall, together with all its dependencies::

    $ easy_install jsonstore

After that, we have a very simple API to create, update, delete and retrieve JSON documents:

    >>> from jsonstore import *
    >>> em = EntryManager('index.db')
    >>> em.create({"type": "people", "name": "Roberto", "age": 29})
    {'age': 29, 'type': 'people', 'name': 'Roberto', '__updated__': datetime.datetime(2008, 2, 4, 11, 26, 32, 438865), '__id__': 'bdce5d77-12a4-4932-a8e6-51acf42b8312'}

Note that the created document receives an automatic id and a timestamp, both which can be overriden. Let's create a couple more of entries:

    >>> em.create(type="pet", name="Chapolim", age=4, __id__='chapolim')
    {'age': 4, 'type': 'pet', 'name': 'Chapolim', '__updated__': datetime.datetime(2008, 2, 4, 11, 29, 24, 155554), '__id__': 'chapolim'}
    >>> em.create({"b": 42}, type=["test", "demo"], a={"foo": "bar"}, __id__='test')
    {'a': {'foo': 'bar'}, 'b': 42, 'type': ['test', 'demo'], '__id__': 'test', '__updated__': datetime.datetime(2008, 2, 4, 11, 29, 55, 347011)}

In order to retrieve a document we need to pass a small JSON object; the entry manager will return all documents that contain the subset:

    >>> em.search(type='pet')
    [{'age': 4, 'type': 'pet', 'name': 'Chapolim', '__updated__': datetime.datetime(2008, 2, 4, 11, 29, 24, 155554), '__id__': 'chapolim'}]
    >>> em.search(a={'foo':'bar'})
    [{'a': {'foo': 'bar'}, 'b': 42, 'type': ['test', 'demo'], '__id__': 'test', '__updated__': datetime.datetime(2008, 2, 4, 11, 29, 55, 347011)}]
    >>> em.search(__id__='chapolim')
    [{'age': 4, 'type': 'pet', 'name': 'Chapolim', '__updated__': datetime.datetime(2008, 2, 4, 11, 29, 24, 155554), '__id__': 'chapolim'}]

This would be somewhat limited, if it weren't for the fact that JSONStore defines some very special operators:

    >>> 1 == LessThan(2)
    True
    >>> "jsonstore" == Like('%json%')
    True
    >>> operators.__all__
    ['Operator', 'Equal', 'NotEqual', 'GreaterThan', 'LessThan', 'GreaterEqual', 'LessEqual', 'Between', 'In', 'Like', 'RegExp', 'Exists']

We can now search for all documents with the name attribute, for example:

    >>> em.search(name=Exists())
    [{'age': 4, 'type': 'pet', 'name': 'Chapolim', '__updated__': datetime.datetime(2008, 2, 4, 11, 29, 24, 155554), '__id__': 'chapolim'}, {'age': 29, 'type': 'people', 'name': 'Roberto', '__updated__': datetime.datetime(2008, 2, 4, 11, 26, 32, 438865), '__id__': 'bdce5d77-12a4-4932-a8e6-51acf42b8312'}]

Or even retrieve recent documents:

    >>> from datetime import datetime
    >>> em.search(__updated__=GreaterThan(datetime(2008, 2, 4, 11, 27)))
    [{'a': {'foo': 'bar'}, 'b': 42, 'type': ['test', 'demo'], '__id__': 'test', '__updated__': datetime.datetime(2008, 2, 4, 11, 29, 55, 347011)}, {'age': 4, 'type': 'pet', 'name': 'Chapolim', '__updated__': datetime.datetime(2008, 2, 4, 11, 29, 24, 155554), '__id__': 'chapolim'}]

This approach is much less powerful than CouchDB's Javascript views, but I'd say it's good enough for writing simple personal Javascript applications. As I said, JSONStore exposes the database to the web using a REST protocol. On top of the REST API, there's a Javascript API and, on top of that, an administrative interface. I'll talk about them on the next part.

Part II. Rest API
-----------------

After describing JSONStore's Python API on part I, I'll now talk about it's REST interface. JSONStore comes with a simple WSGI app based on WebOb; you can get started quickly by running it with the server that comes with Paste::

    $ paster create -t jsonstore store
    $ paster serve store/server.ini

This will give you a store running at http://localhost:8080/. You can edit the ``server.ini`` file to change the host, port, and, most important, the backend (SQLite or MySQL) used by JSONStore. To interact with the store we'll be using my favorite REST client, curl. Let's retrieve a list of the stored documents::

    $ curl http://localhost:8080/
    []

An empty list. We can fix that by adding something::

    $ curl -v http://localhost:8080/ -d '{"type":"test","somevalue":10}'
    HTTP/1.0 201 Created
    Location: http://localhost:8080/a3b7247d-07e4-47da-ab5a-ddd723af8262
    etag: "c47bfabe42ac5291c1f2020657a0efc8d77a724a"
    Content-Length: 122
    content-type: application/json; charset=utf8

    {"somevalue": 10, "type": "test", "__id__": "a3b7247d-07e4-47da-ab5a-ddd723af8262", "__updated__": "2008-02-04T19:02:58Z"}

On the example above I left the interesting response headers:

1. The server replies with a ``201 Created`` status, indicating that the document was, well, created.
2. The ``Location`` header shows the location of the new document, which received an automatically assigned uuid as its id. We can also see the id on the response body, on the ``__id__`` attribute (you can see that I come from a Python background!). The id can be overriden when the object is created by setting this attribute.
3. Etags can be used on ``POST`` to indicate the hash of the newly created resource.
4. ``Content-type`` is ``application/json``.

JSONStore also understands a compact offspring of JSON called Rison. This will be extremely useful later when we search our database, but it also helps when creating documents manually::

    $ curl http://localhost:8080/ -d "(type:test,somevalue:7)"
    {"somevalue": 7, "type": "test", "__id__": "c5ebc899-2319-4493-b3e1-c8d6c8c5e3a6", "__updated__": "2008-02-04T19:21:24Z"}

We can now get a list of all stored documents::

    $ curl http://localhost:8080/
    [...]

If the list is too big it's possible to paginate the results using the ``size`` and ``offset`` query parameters. We can also interact directly with a single document::

    $ curl http://localhost:8080/c5ebc899-2319-4493-b3e1-c8d6c8c5e3a6
    {"somevalue": 7, "type": "test", "__id__": "c5ebc899-2319-4493-b3e1-c8d6c8c5e3a6", "__updated__": "2008-02-04T19:21:24Z"}
    $ curl -X PUT http://localhost:8080/c5ebc899-2319-4493-b3e1-c8d6c8c5e3a6 -d "(type:test,somevalue:5)"
    {"somevalue": 5, "type": "test", "__id__": "c5ebc899-2319-4493-b3e1-c8d6c8c5e3a6", "__updated__": "2008-02-04T19:29:25Z"}
    $ curl -X DELETE http://localhost:8080/c5ebc899-2319-4493-b3e1-c8d6c8c5e3a6

You can use the jsonp or callback query parameter if you want the server to return Javascript code (with the proper ``Content-type`` header, though who cares?) passing the response to your callback function::

    $ curl -v http://localhost:8080/?jsonp=foo
    content-type: text/javascript; charset=utf8

    foo([{"somevalue": 10, "type": "test", "__id__": "a3b7247d-07e4-47da-ab5a-ddd723af8262", "__updated__": "2008-02-04T19:02:58Z"}])

JSON, WSGI, REST, etags, Rison, jsonp... sweet, but what else? Let's take a look at searching now, but first we should add at least one more entry::

    $ curl -v http://localhost:8080/ -d '{"type":"test","somevalue":1}'
    {"somevalue": 1, "type": "test", "__id__": "e0a2b082-d8b7-4afd-aa10-984015adf173", "__updated__": "2008-02-04T19:40:57Z"}

Search works by passing an encoded JSON (or Rison) object on the URL. It's much easier to use Rison here, since it was developed exactly as a way of encoding JSON objects inside URLs; Rison uses tokens that are not escaped in URLs (like parenthesis), and omits quotes where their occurence is unambiguous. If we want to search for objects with the attribute type set to test, we could either do::

    $ curl 'http://localhost:8080/%7B"type"%3A"test"%7D'   # {"type":"test"}
    $ curl "http://localhost:8080/(type%3Atest)"           # (type:test)

More complex queries can be done using operators like ``Equal`` (and ``NotEqual``), ``GreaterThan``, ``GreaterEqual``, ``LessThan``, ``LessEqual``, ``Between``, ``In``, ``Like``, ``RegExp`` and ``Exists``. Here's an example::

    $ curl "http://localhost:8080/(somevalue%3A'Between(5,15)')"
    [{"somevalue": 10, "type": "test", "__id__": "a3b7247d-07e4-47da-ab5a-ddd723af8262", "__updated__": "2008-02-04T19:02:58Z"}]

Although the documents and the search key in these examples are flat, the same process is valid for deep, nested, JSON objects (and keys); the store will returns those documents which contain the search key, using a flexible definition of "contain" when using the operators.

One last interesting thing. Every search returns an ``X-ITEMS`` header, with the total number of documents resulting from the query. This is true even if you pass a ``size=0`` parameter on the query string, so it's an easy way of knowing how many documents match a search without retrieving the data. Another option is doing a ``HEAD`` request.

JSONStore comes with a Javascript API built on top of the REST interface, that allows the development of small Javascript apps with a persistence mechanism. Since the JSONStore database is schema-less (like CouchDB), a single instance of the store can be shared easily between different applications.

Part III. Javascript API
------------------------

Continuing describing JSONStore's API (Python, REST), in this section I'll talk about the Javascript interface to the store. The Javascript API is pretty much a copy of the Python API, so there's isn't much to see here.

The API is defined in the file ``jsonstore.js``, which depends on the official JSON parser/decoder ``json2.js``. The code uses the XML HTTP Request object, so we are bound by the same-host limitation (although the server supports jsonp, as we saw on the last post).

The first step when using the Javascript API is instantiating an entry manager::

    var em = new EntryManager('http://jsonstore.org/');

We can then proceed to create a document::

    em.create({
        name: "John D.",
        interests: ["Python", "Comics"]
    }, {
        success: function(doc) { alert("Ok!") },
        error: function(statusText) { alert("Ops!") }
    });

The create method takes as arguments the document to be created, and an optional dictionary with callback functions for error and success. In case of success, the newly created document (doc) will be passed to the callback function, with an automatically generated id (``__id__``) together with a timestamp (``__updated__``); otherwise, the ``statusText`` is passed to the error callback. The same syntax is used by the update method, the only difference being that the update requires the document id to be set.

The delete method is called remove in the Javascript API, since delete is a reserved word. It requires an id and the two optional callback functions, so to remove a document with the id "foo" we'd do::

    em.remove('foo', { success: function() {}, error: function() {} });

Finally, to search for a document we use the appropriately named search method, passing a subset (the "key") that should match the documents. If we wanted to find book reviews with rating 7 we could do something like this::

    em.search({
        type: "review",
        object: "book",
        rating: 7
    }, {
        size: 10,
        offset: 0,
        success: function(results, total) {},
        error: function(statusText) {}
    });

Note that the success callback receives a list of documents — which could be empty, or have a single element — and the total of results found. The number of results is useful when we specify a limited number of results using the size parameter.

To search for reviews with a small rating, on the other hand, we could use the operator ``LessThan`` and perform a query like this::

    em.search({
        type: "review",
        object: "book",
        rating: "LessThan(3)"
    }, { ... });

If eventually what you really want is to search for documents with an attribute containing the string "LessThan(3)", just wrap it in a ``Equal`` operator::

    em.search({
        foo: "Equal('LessThan(3)')"
    });

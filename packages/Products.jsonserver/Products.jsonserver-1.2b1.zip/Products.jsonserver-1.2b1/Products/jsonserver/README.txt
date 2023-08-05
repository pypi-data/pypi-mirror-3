Based on:

 - original product for earlier versions of Zope2 by Balazs Ree
 - jsonserver for zope3 by Jim Washington jwashin@vt.edu and Contributors
 - ZPublisher/xmlrpc.py

JSON is javascript object notation. JSON-RPC performs the same service
as XML-RPC, except the format is javascript script objects instead of
XML, and the content-type is 'application/json-rpc' instead of 'text/xml'.

This project overrides some base zope2 code to provide the additional
functionality of listening and responding properly to requests of type
"application/json".

This works with Zope 2.10


Installation:
-------------

Add this egg to your Zope/Plone buildout.

Usage:
------

Similar to xmlrpc usage.

jsonserver looks for content-type "application/json", and handles those
requests as JSON-RPC.  Other http requests are not affected and will
presumably work as expected.

XXX JSON-RPC with jQuery

For communication other than in a web browser (javascript), minjson.py
or other json implementations have functions for reading and writing
JSON objects.

The text of a JSON-RPC request looks like::

	{'id':jsonid,''method':remotemethod,'params':methodparams}

where:

    o jsonid is a string or number that may identify this specific request

    o remotemethod is the method to call on the server

    o methodparams is a list(javascript Array) of parameters to the method

The text of a JSON-RPC response looks like::

	{'id':jsonid,''result':returnedresult,'error':returnederr}

where:

    o jsonid is the same jsonid as sent in the request

    o returnedresult is a javascript representation of the result or null

    o returnederr is a javascript representation of an error state

Either returnedresult or returnederr will be the javascript null value.

Actual implementation using e.g., urllib is left as an exercise for the
reader. Hint:  Use the minjson.write(object) and minjson.read(string)
methods for conversion before and after transport.

Five extensions
---------------

The "json" namespace (http://namespaces.zope.org/json) defines the
**page** and **pages** directives. **json:page** is identical to
**browser:page** in the usage, but the page or method declared
is allowed to be called up in a json request, but will be
invisible for normal requests.

**browser:page** and **browser:pages** declarations will be
available to both normal and json requests.

**json:page** declarations will be callable from code and
their macros will be visible from other templates.

TODO:
-----

gzip?

simple-jsonrpc
=============
A python library of JSON-RPC v2.0 specification.


Client Usage
------------

```python
import simplejsonrpc as jsonrpc

server = jsonrpc.Server("http://localhost:8000/rpc")
print server.add(23, 3)
print server.foo()
```


Server
------

wsgi server example:

```python
import simplejsonrpc as jsonrpc

def add(a, b):
    return a + b

def default(*arg, **kwargs):
    return "hello jsonrpc"

class MyJsonrpcHandler(jsonrpc.JsonrpcHandler):
    """define your own dispatcher here"""
    def dispatch(self, method_name):
        if method_name == "add":
            return add
        else:
            return default


def application(environ, start_response):
    # assert environ["REQUEST_METHOD"] = "POST"
    content_length = int(environ["CONTENT_LENGTH"])

    # create a handler
    h = MyJsonrpcHandler()

    # fetch the request body
    request = environ["wsgi.input"].read(content_length)

    # pass the request body to handle() method
    result = h.handle(request)

    #log
    environ["wsgi.errors"].write("request: '%s' | response: '%s'\n" % (request, result))

    start_response("200 OK", [])
    return [result]

from wsgiref.simple_server import make_server
rpcserver = make_server('', 8000, application)
print "Serving on port 8000..."
rpcserver.serve_forever()
```


Installation
------------
You can install this from PyPI with the following command:

    pip install simple-jsonrpc



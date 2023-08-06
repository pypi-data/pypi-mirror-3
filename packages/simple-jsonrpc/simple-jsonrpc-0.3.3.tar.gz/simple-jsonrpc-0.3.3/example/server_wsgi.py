# wsgi jsonrpc handler example
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

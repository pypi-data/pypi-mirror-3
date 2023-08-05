import simplejsonrpc as jsonrpc

server = jsonrpc.Server("http://localhost:8000/rpc")
print server.add(23, 3)
print server.foo()


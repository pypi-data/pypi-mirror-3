# http://groups.google.com/group/json-rpc/web/json-rpc-2-0
# JSON-RPC 2.0 Specification
# Date:	2010-03-26 (based on the 2009-05-24 version)
#
# Homepage: https://github.com/dengzhp/simple-jsonrpc
#
#TODO:
#      multicall

import socket
import sys
from httplib import HTTPConnection
import types
import string
import random
import traceback

# JSON library importing
json = None
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise ImportError(
            'You must have the json, or simplejson ' +
            'module(s) available.'
            )

def jdumps(obj, encoding='utf-8'):
    return json.dumps(obj, encoding=encoding)

def jloads(json_string):
    return json.loads(json_string)


class ProtocolError(Exception):
    pass


class HTTPConnection2(HTTPConnection):
    """add timeout to HTTPConnection for python2.5"""
    def __init__(self, host, port=None, strict=None, timeout=None):
        self.timeout = timeout
        HTTPConnection.__init__(self, host, port, strict)

    def connect(self):
        """Connect to the host and port specified in __init__."""
        msg = "getaddrinfo returns an empty list"
        for res in socket.getaddrinfo(self.host, self.port, 0,
                                      socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                self.sock = socket.socket(af, socktype, proto)
                if self.timeout is not None:
                    self.sock.settimeout(self.timeout)
                if self.debuglevel > 0:
                    print "connect: (%s, %s)" % (self.host, self.port)
                self.sock.connect(sa)
            except socket.error, msg:
                if self.debuglevel > 0:
                    print 'connect fail:', (self.host, self.port)
                if self.sock:
                    self.sock.close()
                self.sock = None
                continue
            break
        if not self.sock:
            raise socket.error, msg


class Transport:
    def __init__(self, host, timeout=None):
        self.host = host
        self.timeout = timeout

    def request(self, handler, request_body):
        if sys.version_info > (2, 6) or self.timeout is None:
            HttpClass = HTTPConnection
        else:
            HttpClass = HTTPConnection2

        if self.timeout is None:
            c = HttpClass(self.host)
        else:
            c = HttpClass(self.host, timeout=self.timeout)
        c.request('POST', handler, request_body)

        r = c.getresponse()
        if r.status != 200:
            raise ProtocolError(r.reason)
        else:
            return r.read()


class _Method:
    # supports "nested" methods (e.g. examples.getStateName)
    def __init__(self, send, name):
        self.__send = send
        self.__name = name

    def __call__(self, *args, **kwargs):
        if len(args) > 0 and len(kwargs) > 0:
            raise ProtocolError('Cannot use both positional ' +
                'and keyword arguments (according to JSON-RPC spec.)')
        if len(args) > 0:
            return self.__send(self.__name, args)
        else:
            return self.__send(self.__name, kwargs)

    def __getattr__(self, name):
        self.__name = '%s.%s' % (self.__name, name)
        return self


class _Notify:
    def __init__(self, send):
        self._send = send

    def __getattr__(self, name):
        return _Method(self._send, name)


def error(code=32000, msg="Server error", data=None):
    err = {}
    err["code"] = code
    err["message"] = msg
    if data:
        err["data"] = data
    return err


class ServerProxy:
    def __init__(self, uri, encoding='utf-8', timeout=None):
        import urllib

        schema, uri = urllib.splittype(uri)
        if schema != 'http':
            raise IOError('Unsupported JSON-RPC protocol.')
        self.__host, self.__handler = urllib.splithost(uri)
        if not self.__handler:
            #raise Exception?
            self.__handler = '/'

        self.__transport = Transport(self.__host, timeout=timeout)
        self.__encoding = encoding

    def __str__(self):
        return "<jsonrpc.ServerProxy instance('%s%s')>" % (self.__host, self.__handler)

    def _request(self, methodname, params, rpcid=None):
        request = dumps(params, methodname, encoding=self.__encoding,
                        rpcid=rpcid)

        response = self.__transport.request(self.__handler,
                                            request)
        r = loads(response)
        check_for_errors(r)
        return r['result']

    def _request_notify(self, methodname, params, rpcid=None):
        request = dumps(params, methodname, encoding=self.__encoding,
                        rpcid=rpcid, notify=True)
        response = self.__transport.request(self.__handler,
                                            request)
        ## check?
        #r = loads(response)
        #check_for_errors(r)

    def __getattr__(self, name):
        return _Method(self._request, name)

    @property
    def _notify(self):
        return _Notify(self._request_notify)

Server = ServerProxy


IDCHARS = string.ascii_lowercase+string.digits
def random_id(length=8):
    return_id = ''
    for i in range(length):
        return_id += random.choice(IDCHARS)
    return return_id


def dumps(params=[], methodname=None, methodresponse=False,
          encoding='utf-8', rpcid=None, notify=None, error=False):

    s = {"jsonrpc": "2.0"}

    if methodresponse:
        if rpcid is None and not error:
            raise ValueError('A method response must have an rpcid.')

        if not error:
            s["result"] = params
        else:
            s["error"] = params
        s["id"] = rpcid
        return jdumps(s, encoding=encoding)

    else:
        if type(methodname) not in types.StringTypes:
            raise ValueError('Method name must be a string')

    valid_params = (types.TupleType, types.ListType, types.DictType)
    if type(params) not in valid_params:
        raise TypeError('Params must be a dict, list, tuple')

    s["method"] = methodname
    if params:
        s["params"] = params

    if not notify:
        if rpcid:
            s["id"] = rpcid
        else:
            s["id"] = random_id()

    return jdumps(s, encoding=encoding)


def loads(data):
    if not data:
        # notification
        return None
    result = jloads(data)
    return result


def check_for_errors(result):
    if not result:
        # Notification
        return result
    if type(result) is not types.DictType:
        raise TypeError('Response is not a dict.')
    if 'jsonrpc' not in result.keys() or float(result['jsonrpc']) != 2.0:
        raise NotImplementedError('JSON-RPC version not supported.')
    if 'result' not in result.keys() and 'error' not in result.keys():
        raise ValueError('Response does not have a result or error key.')
    if 'error' in result.keys() and result['error'] != None:
        code = result['error']['code']
        message = result['error']['message']
        raise ProtocolError((code, message))
    return result


class JsonrpcHandler:

    def dispatch(self, method_name):
        """Please overwrite me!! return a function"""
        return None

    def _validate_request(self):
        if type(self._request) is not types.DictType:
            return False
        if "jsonrpc" not in self._request.keys() or \
                self._request["jsonrpc"] != "2.0":
            return False

        self._method = self._request.get("method", None)
        self._rpcid = self._request.get("id", None)
        self._params = self._request.get("params", [])

        param_types = (types.ListType, types.DictType, types.TupleType)
        if not self._method or type(self._method) not in types.StringTypes or \
                type(self._params) not in param_types:
            return False
        return True

    def handle(self, request):
        try:
            self._request = loads(request)
        except Exception, e:
            err = error(-32700, "Parse error")
            return dumps(params=err, methodresponse=True, error=True)

        if not self._validate_request():
            err = error(-32600, "Invalid Request")
            return dumps(params=err, methodresponse=True, error=True)

        func = self.dispatch(self._method)
        if not func:
            err = error(-32601, "Method not found")
            return dumps(params=err, methodresponse=True, error=True)

        try:
            if type(self._params) is types.ListType:
                result = func(*self._params)
            else:
                result = func(**self._params)
        except TypeError:
            err = error(-32602, "Invalid params")
            return dumps(params=err, methodresponse=True, error=True)
        except:
            err_lines = traceback.format_exc().splitlines()
            trace_string = '%s | %s' % (err_lines[-3], err_lines[-1])

            err = error(-32603, "Internal error: %s" % trace_string)
            return dumps(params=err, methodresponse=True, error=True)

        return dumps(params=result, methodresponse=True, rpcid=self._rpcid)


'''
Copyright 2012 Research Institute eAustria

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Marian Neagul <marian@ieat.ro>
@contact: marian@ieat.ro
@copyright: 2012 Research Institute eAustria
'''

from jsonrpc2 import JsonRpcBase, JsonRpcException
import functools
import uuid
import socket
import json
import logging
import SocketServer
import threading


class RPCException(Exception):
    pass

def jsonmethod(func):
    @functools.wraps(func)
    def __wrapper(*p, **kw):
        return func(*p, **kw)
    setattr(__wrapper, '_jsonrpc_method', True)
    setattr(__wrapper, '_jsonrpc_instance', False)
    return __wrapper

def jsonattribute(name, **kw):
    def __outer_wr(func):
        attr_map = {} # contains entry's like {'kind': type, 'default':}, default being optional
        if hasattr(func, '_wrap_info'):
            wrap_info = getattr(func, '_wrap_info')
        else:
            wrap_info = {}
            setattr(func, '_wrap_info', wrap_info)
        if '_jsonrpc_parameter_map' in wrap_info:
            attr_map = wrap_info['_jsonrpc_parameter_map']
        else:
            wrap_info['_jsonrpc_parameter_map'] = attr_map

        if name in attr_map:
            raise AssertionError('Attribute `%s` already defined' % name)
        else:
            entry = {'kind': kw.get('kind', object).__name__,
                     'documentation': kw.get('documentation', None)}
            attr_map[name] = entry
            if 'default' in kw:
                entry['default'] = kw.get('default')
        if '_jsonrpc_wrapped_function' in wrap_info:
            wrap_func = wrap_info['_jsonrpc_wrapped_function']
        else:
            @functools.wraps(func)
            def __inner_wr(self, *p, **ikw):
                attr_map = __inner_wr._wrap_info['_jsonrpc_parameter_map']
                code = func.__code__
                func_defaults = func.func_defaults
                args = code.co_varnames[1:code.co_argcount]
                if len(code.co_varnames) < 1:
                    raise NotImplementedError("Decorator is designed for methods and not for plain functions")
                self_name = code.co_varnames[0]
                for arg in attr_map.keys():
                    if arg not in args:
                        raise AssertionError('Parameter `%s` is not handled by method' % arg)

                for arg in ikw.keys():
                    if arg not in attr_map:
                        raise AttributeError('Supplied parameter `%s` is not handled by method' % arg)

                if self_name in attr_map:
                    raise AssertionError('Parameter name `%s` is special for method' % self_name)

                efective_params = {}

                for i in range(len(args)):
                    arg_name = args[i]
                    if arg_name in ikw:
                        arg_value = ikw[arg_name]
                    else:
                        if func_defaults is None or i > len(func_defaults):
                            raise AttributeError("No value supplied for mandatory attribute `%s`" % arg_name)
                        arg_value = func_defaults[i - 1]
                    # ToDo: arguments should be validated by type also
                    efective_params[arg_name] = arg_value


                rez = func(self, *p, **efective_params) # ToDO: we should implement also positional arguments
                return rez
            wrap_func = __inner_wr
            wrap_info['_jsonrpc_wrapped_function'] = __inner_wr
        return wrap_func
    return __outer_wr


class Wrapper(object):
    def __init__(self, obj):
        self._wrapped_object = obj
        self._jsonrpc_instance = True

    def __call__(self, *args, **argv):
        self._wrapped_object(*args, **argv)

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        else:
            return getattr(self._wrapped_object, attr)

def jsoninst(inst):
    wrapped = Wrapper(inst)
    wrapped._jsonrpc_method = True
    return wrapped


def isrpcmethod(obj):
    return getattr(obj, '_jsonrpc_method', False)

def build_exception(msg, extra = None):
    code = msg['code']
    message = msg["message"]
    text = "(%d) %s" % (code, message)
    if extra is not None:
        text = text + ": %s" % extra
    exception = RPCException(text)
    return exception


class RPCBase(object):
    def __init__(self):
        self._jsonrpc_method = True
        self.methods = self._get_methods()
        self.log = logging.getLogger(__name__)

    def add_method(self, name, meth):
        self.log.debug("adding %s as %s", meth, name)

        if not isinstance(meth, RPCBase):
            self.log.info("Unsupported type: %s", type(meth))
            raise NotImplementedError("Unsupported type: `%s`" % type(meth))

        if hasattr(self, name):
            raise AttributeError("Method `%s` already defined!" % name)
        setattr(self, name, jsoninst(meth))

        self.methods = self._get_methods()

    def _get_methods(self, obj = None):
        if obj is None:
            obj = self
        meths = {}
        for attrName in dir(obj):
            attr = getattr(obj, attrName)
            if not isrpcmethod(attr):
                continue
            meths[attrName] = attr
        return meths

    @jsonmethod
    def rpc_methods(self):
        """Return a list with all RPC methods registered in his context
        """
        meths = self.methods.keys()
        result = {}
        for met in meths:
            desc = {}
            m = getattr(self, met)
            desc['documentation'] = m.__doc__
            if m._jsonrpc_instance:
                desc['type'] = 'instance'
            else:
                desc['type'] = 'callable'
            if hasattr(m, '_wrap_info'):
                desc['argument_specification'] = m._wrap_info.get('_jsonrpc_parameter_map', {})
            else:
                desc['argument_specification'] = {}
            result[met] = desc
        return result

class DummyTransport(object):
    def __init__(self, rpcImpl):
        self._rpcImpl = rpcImpl
        self.log = logging.getLogger("DummyTransport")

    def rpc_send_message(self, msg):
        try:
            rez = self._rpcImpl.process(msg, {})
        except JsonRpcException, e:
            self.log.exception("Error processing call")
            rez = e.as_dict()
        return rez

class UnixStreamTransport(object):
    def __init__(self, endpoint):
        self._endpoint = endpoint
        self.log = logging.getLogger("UnixStreamTransport")

    def rpc_send_message(self, msg):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self._endpoint)
        fd = sock.makefile()
        log = self.log
        try:
            payload = json.dumps(msg)
            req_size = len(payload)
            fd.write("Request-Size: %d\n" % req_size)
            fd.write("\n")
            fd.write(payload)
            fd.flush()
            payloadSize = None
            while True:
                line = fd.readline()
                if len(line) == 0:
                    self.log.debug("End parsing headers")
                    break
                line = line.strip("\n").strip("\r")
                if len(line) == 0:
                    self.log.debug("Headers finish mark hit")
                    break
                self.log.debug("Header: %s", line)
                header_line = line.split(":", 1)
                if len(header_line) != 2:
                    log.error("Invalid header line: %s", line)
                header, value = header_line
                if header == "Status":
                    value_s = value.strip().split()
                    if len(value_s) < 1:
                        log.error("Invalid response from server")
                        return # ToDo: raise error ?
                    code = int(value_s[0])
                    if code < 200 or code >= 300 :
                        log.error("Server failed to perform")
                    else:
                        log.debug("Server succesfuly handled the request")
                elif header == "Response-Size":
                    payloadSize = int(value)
            if payloadSize is None:
                log.error("Server did not return response size")
                return # ToDo: thow an error
            response = fd.read(payloadSize)
            self.log.debug("Response from server is: %s", response)
            js = json.loads(response)
            log.debug("Server replied with: %s", js)
            return js

        finally:
            fd.flush()
            sock.close()

class RPCProxy(object):
    def __init__(self, transport, prefix = None):
        self.log = logging.getLogger("RPCProxy")
        self.__transport = transport
        self._methods = None
        self.prefix = prefix
        self.__update_methods()

    def get_proxy(self, prefix):
        self.log.debug("Current proxy prefix is %s", self.prefix)
        if self.prefix is not None:
            new_prefix = ".".join([self.prefix, prefix])
        else:
            new_prefix = prefix
        self.log.debug("Prefix for new proxy is %s", new_prefix)
        return RPCProxy(self.__transport, new_prefix)

    def __wrap_remote_func(self, name):
        def __wrapper(*args, ** kw):
            ret = self.__call_method(name, *args, **kw)
            if 'error' in ret:
                raise build_exception(ret['error'], name)
            return ret['result']
        return __wrapper

    def __wrap_remote_inst(self, name):
        self.log.debug("Wrapping remote instance for %s", name)
        return self.get_proxy(name)

    def __update_methods(self):
        result = self.__call_method('rpc_methods')
        self._methods = result['result']
        for meth in self._methods.keys():
            meth_type = self._methods[meth].get('type', 'callable')
            if meth_type == 'callable':
                entry = self.__wrap_remote_func(meth)
            elif meth_type == 'instance':
                self.log.debug("Registering %s as instance", meth)
                entry = self.__wrap_remote_inst(meth)
            else:
                raise RPCException('Unsupported method type')
            entry.__doc__ = self._methods[meth].get('documentation', None)
            setattr(self, meth, entry)

    def __call_method(self, name, *args, **kw):
        if self.prefix is not None:
            meth_name = ".".join([self.prefix, name])
        else:
            meth_name = name

        call_values = {'jsonrpc':'2.0',
                       'method':meth_name,
                       'params': kw,
                       'id': uuid.uuid4().get_hex()}
        self.log.debug("Efective JSON before dispatching is: %s", call_values)
        result = self.__send_msg(call_values)
        self.log.debug("Result after call is: %s", result)
        if result is None:
            raise RPCException("No result from server")
        if "error" in result:
            raise build_exception(result["error"], name)
        return result

    def __send_msg(self, msg):
        return self.__transport.rpc_send_message(msg)

class RPCService(JsonRpcBase):
    def __init__(self, obj):
        self._obj = obj
        self.methods = obj._get_methods()
        self._maps = {}
        self.log = logging.getLogger("RPCService")

    def process(self, data, extra_vars):
        raw_path = data["method"]
        path = raw_path.split(".")
        efective_method = path[-1]
        if len(path) == 1:
            self.log.debug("Processing on own object")
            return JsonRpcBase.process(self, data, extra_vars)
        elif len(path) == 0:
            self.log.critical("Invalid specification of method %s", raw_path)
            raise AttributeError("Invalid specification of method %s", raw_path)

        if raw_path in self._maps:
            self.log.debug("Hit from cache for %s", raw_path)
            data["method"] = efective_method
            return self._maps[raw_path].process(data, extra_vars)

        inst = path[0]
        meth = path[1:]
        if hasattr(self._obj, inst):
            rpcs = RPCService(getattr(self._obj, inst))
            self._maps[raw_path] = rpcs
            data["method"] = ".".join(meth)
            return rpcs.process(data, extra_vars)
        else:
            raise AttributeError("No such attribute %s in service" % inst)


class ThreadedUnixServer(SocketServer.ThreadingMixIn, SocketServer.UnixStreamServer):
    allow_reuse_address = True


class BaseJSONDispatcher(object):
    log = logging.getLogger("BaseJSONDispatcher")

    def dispatch(self, js, rpc = None):
        log = self.log.getChild("dispatch")
        log.debug("Dispatching JSON: %s" % js)
        if rpc is None and hasattr(self, "_rpc"):
            rpc = self._rpc
        if rpc is None:
            log.critical("Internal error! No available rpc !")
        result = rpc.process(js, {})
        log.debug("Dispatching completed")
        return result


class BaseConnector(object):
    pass

class UnixSocketConnector(threading.Thread):
    log = logging.getLogger("UnixSocketConnector")
    def __init__(self, rpc, socket_path):
        threading.Thread.__init__(self)
        self._rpc = rpc
        self._socket_path = socket_path
        self._server = self.get_server()

    def run(self):
        server_thread = threading.Thread(target = self._server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

    def get_server(self):
        server = ThreadedUnixServer(self._socket_path, self._get_request_handler())
        return server

    def _get_request_handler(self):
        rpc = self._rpc
        _log = self.log
        class __RequestHandler(SocketServer.BaseRequestHandler, BaseJSONDispatcher):
            _rpc = rpc
            log = _log.getChild("RequestHandler")

            def __init__(self, *args, **kw):
                self._sent_headers = []
                BaseJSONDispatcher.__init__(self)
                SocketServer.BaseRequestHandler.__init__(self, *args, **kw)

            def send_header(self, io, header, value):
                io.write("%s: %s\n" % (header, value))
                self._sent_headers.append(header)

            def send_data(self, io, data):
                if self._sent_headers:
                    io.write("\n")
                else:
                    self.log.critical("Sending data without headers... Stupid but obeying the user")
                io.write(data)

            def handle(self):
                log = self.log
                sock = self.request
                f = sock.makefile()
                payloadSize = None
                log.debug("Handling new request from: %s", self.client_address)
                try:
                    while True:
                        line = f.readline().strip("\n").strip("\r")
                        if len(line) == 0:
                            break
                        header_line = line.split(":", 1)
                        if len(header_line) != 2:
                            continue
                        header, value = header_line
                        if header == 'Request-Size':
                            payloadSize = int(value)
                        else:
                            log.debug("Unsupported header %s", header)
                    payload = f.read(payloadSize)
                    try:
                        js = json.loads(payload)
                        log.debug("JSON Parsed corectly: %s", js)
                    except ValueError:
                        log.exception("Could not parse JSON")
                        self.send_header(f, "Status", "JSON Error")
                        return
                    log.debug("Dispatching request to JSONRpc handler")
                    try:
                        result = self.dispatch(js, self._rpc)
                    except JsonRpcException, e:
                        log.exception("Could not process request from %s", self.client_address)
                        self.send_header(f, "Status", "500 Could not dispatch")
                        result = e.as_dict()
                    else:
                        self.send_header(f, "Status", "200 Dispatched OK")
                        log.debug("Dispatch was successful")
                    data = json.dumps(result)
                    self.send_header(f, "Response-Size", "%s" % len(data))
                    self.send_data(f, data)
                finally:
                    f.flush()
                    f.close()
        return __RequestHandler

# coding: utf-8
"""greenet is a gevent-based python networking library."""
from gevent import socket
from gevent.server import StreamServer
from gevent.queue import Queue
from gevent.event import AsyncResult
import gevent
import jsonpack

__version__ = '0.1a'
__all__ = ['GreenServer', 
           'JsonTransport', 
           'EchoServer', 
           'SessionPool', 
           'IDGenerator',
           ]

#TODO: WebSocketTransport

def IDGenerator():
    i = 0
    wall = 1 << 31
    while True:
        i += 1
        if i > wall:
            i = 1
        yield i

class SessionPool:
    _iter = IDGenerator()
    sessions = {}
    
    @classmethod
    def put(cls, trans):
        sid = cls._iter.next()
        cls.sessions[sid] = trans
        return sid
    
    @classmethod
    def pop(cls, sid):
        return cls.sessions.pop(sid, None)

    @classmethod
    def get(cls, sid):
        return cls.sessions.get(sid, None)

    @classmethod
    def size(cls):
        return len(cls.sessions)

def clearqueue(q):
    while not q.empty():
        q.get_nowait()

class Transport:
    """<传输器> 对socket对象的包装, 提供了一致的消息收发和关闭连接的接口.
    .. 本类收发的是字节数据, 可继承recv_filter和send_filter实现自定的消息格式.
    
    - heartbeat: 数字表示心跳超时秒数, 不计时用None.
    """
    def __init__(self, sock, heartbeat=None):
        assert sock, 'Empty sock.'
        self.sock = sock
        self.heartbeat = heartbeat
        self.sid = SessionPool.put(self)
        self.peer = sock.getpeername()
        self.queue = Queue()
        self.receiver = gevent.spawn(self._process_recv)
    
    @property
    def dead(self):
        return not SessionPool.get(self.sid)
    
    def _process_recv(self):
        while True:
            if self.dead: return
            try:
                data = None
                with gevent.Timeout(self.heartbeat, False):
                    data = self.sock.recv(8192)
                if not data: break
                value = self.recv_filter(data)
                if isinstance(value, list):
                    for chunk in value:
                        self.queue.put(('recv', chunk))
                else:
                    self.queue.put(('recv', value))
                del data, value
            except socket.error:
                break
        self.queue.put(('close', 0))

    def recv_filter(self, data):
        "data -> value"
        return data

    def send_filter(self, value):
        "value -> data"
        return value

    def _wait(self):
        "等待消息, 返回空表示断线"
        while True:
            if self.dead: return
            op, value = self.queue.get()
            if op == 'send':
                data = self.send_filter(value)
                self.sock.sendall(data)
            elif op == 'recv':
                if value: return value
            elif op == 'write':
                self.sock.sendall(value)
            elif op == 'close':
                return
            else:
                assert False, 'Should not be to here! %r, %r' % (op, value)

    def recv(self, timeout=None):
        "参数timeout如果是数字就是超时秒数,None是不计时"
        try:
            result = None
            with gevent.Timeout(timeout, False):
                result = self._wait()
            return result
        except socket.error: # 如果队列消息积累过多并且这时socket已关闭了就会报错说文件描述符被关闭,这种错误应该忽略并退出.
            return

    def send(self, value):
        if self.dead: return
        self.queue.put(('send', value))

    def write(self, data):
        "send bytes-oriented data"
        self.queue.put(('write', data))

    def close(self):
        clearqueue(self.queue)
        self.queue.put(('close', 0))
        SessionPool.pop(self.sid)
        self.receiver.kill()
        self.sock.close()

class JsonTransport(Transport):
    """消息以json字典为单位. 
    """
    def __init__(self, sock, timeout=None):
        Transport.__init__(self, sock, timeout)
        self.unpacker = jsonpack.Unpacker()
    
    def recv_filter(self, data):
        return self.unpacker.feed(data)

    def send_filter(self, value):
        return jsonpack.encode(value)


def assertport(port):
    "断言端口是否可绑定."
    sock = socket.socket()
    try:
        sock.bind(('', port))
    except socket.error:
        raise AssertionError('Port already in use %s' % port)
    finally:
        sock.close()

class GreenServer(StreamServer):
    """基于gevent的简单服务器类.
    
    - transport_class: 选择使用哪种传输器,不同传输器导致收发消息格式不同.
    - ssl_args: 使用ssl 请加参数keyfile='server.key',certfile='server.crt'.
    - self.setopt(heartbeat=5): 设置心跳超时秒数,None为不计时.
    
    .. 例子:
        >>> server = GreenServer(5555, Transport)
        >>> server.serve_forever()
    """
    def __init__(self, port, transport_class=Transport, **ssl_args):
        StreamServer.__init__(self, ('', port), **ssl_args)
        self.transport_class = transport_class
        self.heartbeat = None
        self.sessions = {}
        self.debug = True

    def handle(self, sock, address):
        trans = self.transport_class(sock, self.heartbeat)
        self.sessions[trans.sid] = trans
        self.onopen(trans)
        
        try:
            while True:
                chunk = trans.recv()
                if not chunk: break
                self.onmessage(trans, chunk)
        finally:
            trans.close()
            self.sessions.pop(trans.sid, None)
            self.onclose(trans)
            del trans

    def onopen(self, trans):
        pass
    
    def onclose(self, trans):
        pass
    
    def onmessage(self, trans, chunk):
        pass

    def setopt(self, **kw):
        heartbeat = kw.get('heartbeat', None)
        if heartbeat:
            self.heartbeat = heartbeat

    def getopt(self, optname):
        if optname == 'heartbeat':
            return self.heartbeat

    def start(self):
        assertport(self.server_port)
        StreamServer.start(self)

class EchoServer(GreenServer):
    def onmessage(self, trans, chunk):
        trans.send(chunk)
    
    def onopen(self, trans):
        print 'open ', len(self.sessions)
    
    def onclose(self, trans):
        print 'close', len(self.sessions)

def create_connection(address, transport_class, **ssl_args):
    "连接地址address, 返回一个客户端Transport"
    try:
        sock = socket.socket()
        if ssl_args:
            from gevent.ssl import wrap_socket
            sock = wrap_socket(sock, **ssl_args)
        sock.connect(address)
    except socket.error, e:
        sock.close()
        raise socket.error, e
    trans = transport_class(sock)
    return trans


class StructObject:
    """单层(无嵌套)字典转对象.
    """
    def __init__(self, entries):
        self.__dict__.update(entries)
    
    def __str__(self):
        return '<StructObject %s>' % str(self.__dict__)

class RPCError(Exception):
    pass

class RPCClient:
    """RPC客户端
    
    .. 例子:
        >>> rpc = RPCClient(('localhost', 5555))
        >>> print rpc.Echo('hi')
        hi
    """
    def __init__(self, address, transport_class=JsonTransport):
        self.tasks = {}
        self.api = ''
        self._iter = IDGenerator()
        self.trans = create_connection(address, transport_class)
        gevent.spawn(self.handle, self.trans)
    
    def __str__(self):
        return '<RPCClient server=%s>' % str(self.trans.peer)
    
    def handle(self, trans):
        try:
            while True:
                msg = trans.recv()
                if not msg: break
                self.onmessage(msg)
        finally:
            trans.close()
    
    def onmessage(self, msg):
        id     = msg.get('id', None)
        if id == None: return
        value  = msg.get('value', None)
        error  = msg.get('error', None)
        result = self.tasks.pop(id, None)
        if not result: return
        if error:
            result.set_exception(RPCError(str(error)))
        else:
            result.set(value)

    def __getattr__(self, api):
        self.api = api
        return self._call

    def _call(self, *args, **kw):
        """三个可选参数:
        - block: 默认True阻塞, False只请求不等结果.
        - timeout: 在阻塞打开的情况下最大等待秒数,默认None不计时.
        - asobj: 是否把返回结果转换成对象(只有字典可以),默认False不转换.
        """
        assert not self.trans.dead
        block = kw.pop('block', True)
        timeout = kw.pop('timeout', None)
        asobj = kw.pop('asobj', False)
        id = self._iter.next()
        msg = {'id':id, 'api':self.api, 'args':args, 'kwargs':kw}
        self.trans.send(msg)
        if not block: return
        result = AsyncResult()
        self.tasks[id] = result
        value = result.get(timeout=timeout)
        if asobj:
            value = StructObject(value)
        return value

    def close(self):
        self.tasks = {}
        self.trans.close()

def findport(startport, maxtrytimes=10000):
    """
    find out a free port number on your system starting at *startport*,
    if fail return 0.
    """
    port = startport
    sock = socket.socket()
    for i in xrange(maxtrytimes):
        try:
            sock.bind(('', port))
            break
        except socket.error:
            port += 1
    else:
        port = 0
    sock.close()
    return port

if __name__ == '__main__':    
    import os
    server = EchoServer(5555, JsonTransport)
    server.debug = 0
    server.setopt(heartbeat=10)
    print server, os.getpid()
    server.serve_forever()

import unittest

class TestHTTPChannel(unittest.TestCase):
    def _makeOne(self, sock, addr, adj, map=None):
        from waitress.channel import HTTPChannel
        server = DummyServer()
        return HTTPChannel(server, sock, addr, adj=adj, map=map)

    def _makeOneWithMap(self, adj=None):
        if adj is None:
            adj = DummyAdjustments()
        sock = DummySock()
        map = {}
        inst = self._makeOne(sock, '127.0.0.1', adj, map=map)
        return inst, sock, map

    def test_ctor(self):
        inst, _, map = self._makeOneWithMap()
        self.assertEqual(inst.addr, '127.0.0.1')
        self.assertEqual(map[100], inst)

    def test_writable_no_task_will_close(self):
        inst, sock, map = self._makeOneWithMap()
        inst.task = None
        inst.will_close = True
        inst.outbuf = ''
        self.assertTrue(inst.writable())

    def test_writable_no_task_outbuf(self):
        inst, sock, map = self._makeOneWithMap()
        inst.task = None
        inst.will_close = False
        inst.outbuf ='a'
        self.assertTrue(inst.writable())

    def test_writable_with_task(self):
        inst, sock, map = self._makeOneWithMap()
        inst.task = True
        self.assertFalse(inst.writable())

    def test_handle_write_with_task(self):
        inst, sock, map = self._makeOneWithMap()
        inst.task = True
        inst.last_activity = 0
        result = inst.handle_write()
        self.assertEqual(result, None)
        self.assertEqual(inst.last_activity, 0)

    def test_handle_write_no_task_with_outbuf(self):
        inst, sock, map = self._makeOneWithMap()
        inst.task = None
        inst.outbuf = DummyBuffer(b'abc')
        inst.last_activity = 0
        result = inst.handle_write()
        self.assertEqual(result, None)
        self.assertNotEqual(inst.last_activity, 0)
        self.assertEqual(sock.sent, b'abc')

    def test_handle_write_no_task_with_outbuf_raises_socketerror(self):
        import socket
        inst, sock, map = self._makeOneWithMap()
        inst.task = None
        L = []
        inst.log_info = lambda *x: L.append(x)
        inst.outbuf = DummyBuffer(b'abc', socket.error)
        inst.last_activity = 0
        result = inst.handle_write()
        self.assertEqual(result, None)
        self.assertNotEqual(inst.last_activity, 0)
        self.assertEqual(sock.sent, b'')
        self.assertEqual(len(L), 1)

    def test_handle_write_no_task_no_outbuf_will_close(self):
        inst, sock, map = self._makeOneWithMap()
        inst.task = None
        inst.outbuf = None
        inst.will_close = True
        inst.last_activity = 0
        result = inst.handle_write()
        self.assertEqual(result, None)
        self.assertEqual(inst.connected, False)
        self.assertEqual(sock.closed, True)
        self.assertNotEqual(inst.last_activity, 0)

    def test_readable_no_task_not_will_close(self):
        inst, sock, map = self._makeOneWithMap()
        inst.task = None
        inst.will_close = False
        self.assertEqual(inst.readable(), True)

    def test_readable_no_task_will_close(self):
        inst, sock, map = self._makeOneWithMap()
        inst.task = None
        inst.will_close = True
        self.assertEqual(inst.readable(), False)

    def test_readable_with_task(self):
        inst, sock, map = self._makeOneWithMap()
        inst.task = True
        self.assertEqual(inst.readable(), False)

    def test_readable_with_nonempty_inbuf_calls_received(self):
        inst, sock, map = self._makeOneWithMap()
        L = []
        inst.received = lambda: L.append(True)
        inst.task = None
        inst.inbuf = True
        self.assertEqual(inst.readable(), True)
        self.assertEqual(len(L), 1)

    def test_handle_read_no_error(self):
        inst, sock, map = self._makeOneWithMap()
        inst.will_close = False
        inst.recv = lambda *arg: b'abc'
        inst.last_activity = 0
        result = inst.handle_read()
        self.assertEqual(result, None)
        self.assertNotEqual(inst.last_activity, 0)
        self.assertEqual(inst.inbuf.get(100), b'abc')

    def test_handle_read_error(self):
        import socket
        inst, sock, map = self._makeOneWithMap()
        inst.will_close = False
        def recv(b): raise socket.error
        inst.recv = recv
        L = []
        inst.log_info = lambda *x: L.append(x)
        inst.last_activity = 0
        result = inst.handle_read()
        self.assertEqual(result, None)
        self.assertEqual(inst.last_activity, 0)
        self.assertEqual(len(L), 1)
        self.assertEqual(inst.inbuf.get(100), b'')

    def test_write_empty_byte(self):
        inst, sock, map = self._makeOneWithMap()
        wrote = inst.write(b'')
        self.assertEqual(wrote, 0)

    def test_write_nonempty_byte(self):
        inst, sock, map = self._makeOneWithMap()
        wrote = inst.write(b'a')
        self.assertEqual(wrote, 1)

    def test_write_outbuf_gt_send_bytes_has_data(self):
        from waitress.adjustments import Adjustments
        class DummyAdj(Adjustments):
            send_bytes = 10
        inst, sock, map = self._makeOneWithMap(adj=DummyAdj)
        wrote = inst.write(b'x' * 1024)
        self.assertEqual(wrote, 1024)

    def test_write_outbuf_gt_send_bytes_no_data(self):
        from waitress.adjustments import Adjustments
        class DummyAdj(Adjustments):
            send_bytes = 10
        inst, sock, map = self._makeOneWithMap(adj=DummyAdj)
        inst.outbuf.append(b'x' * 20)
        self.connected = False
        wrote = inst.write(b'')
        self.assertEqual(wrote, 0)

    def test__flush_some_notconnected(self):
        inst, sock, map = self._makeOneWithMap()
        inst.outbuf = b'123'
        inst.connected = False
        result = inst._flush_some()
        self.assertEqual(result, False)

    def test__flush_some_empty_outbuf(self):
        inst, sock, map = self._makeOneWithMap()
        inst.connected = True
        result = inst._flush_some()
        self.assertEqual(result, False)

    def test__flush_some_full_outbuf_socket_returns_nonzero(self):
        inst, sock, map = self._makeOneWithMap()
        inst.connected = True
        inst.outbuf.append(b'abc')
        result = inst._flush_some()
        self.assertEqual(result, True)

    def test__flush_some_full_outbuf_socket_returns_zero(self):
        inst, sock, map = self._makeOneWithMap()
        sock.send = lambda x: False
        inst.connected = True
        inst.outbuf.append(b'abc')
        result = inst._flush_some()
        self.assertEqual(result, False)

    def test_handle_close_no_task(self):
        inst, sock, map = self._makeOneWithMap()
        inst.task = None
        inst.handle_close()
        self.assertEqual(inst.connected, False)
        self.assertEqual(sock.closed, True)

    def test_handle_close_with_task(self):
        inst, sock, map = self._makeOneWithMap()
        inst.task = True
        inst.handle_close()
        self.assertEqual(inst.will_close, True)

    def test_add_channel(self):
        inst, sock, map = self._makeOneWithMap()
        fileno = inst._fileno
        inst.add_channel(map)
        self.assertEqual(map[fileno], inst)
        self.assertEqual(inst.server.active_channels[fileno], inst)

    def test_del_channel(self):
        inst, sock, map = self._makeOneWithMap()
        fileno = inst._fileno
        inst.server.active_channels[fileno] = True
        inst.del_channel(map)
        self.assertEqual(map.get(fileno), None)
        self.assertEqual(inst.server.active_channels.get(fileno), None)

    def test_received(self):
        inst, sock, map = self._makeOneWithMap()
        inst.server = DummyServer()
        inst.inbuf.append(b'GET / HTTP/1.1\n\n')
        inst.received()
        self.assertEqual(inst.server.tasks, [inst])
        self.assertTrue(inst.task)

    def test_received_with_task(self):
        inst, sock, map = self._makeOneWithMap()
        inst.task = True
        self.assertEqual(inst.received(), False)

    def test_received_no_chunk(self):
        inst, sock, map = self._makeOneWithMap()
        self.assertEqual(inst.received(), False)

    def test_received_preq_not_completed(self):
        inst, sock, map = self._makeOneWithMap()
        inst.server = DummyServer()
        preq = DummyParser()
        inst.request = preq
        preq.completed = False
        preq.empty = True
        inst.inbuf.append(b'GET / HTTP/1.1\n\n')
        inst.received()
        self.assertEqual(inst.task, None)
        self.assertEqual(inst.server.tasks, [])

    def test_received_preq_completed_empty(self):
        inst, sock, map = self._makeOneWithMap()
        inst.server = DummyServer()
        preq = DummyParser()
        inst.request = preq
        preq.completed = True
        preq.empty = True
        inst.inbuf.append(b'GET / HTTP/1.1\n\n')
        inst.received()
        self.assertEqual(inst.request, None)
        self.assertEqual(inst.server.tasks, [])

    def test_received_preq_error(self):
        inst, sock, map = self._makeOneWithMap()
        inst.server = DummyServer()
        preq = DummyParser()
        inst.request = preq
        preq.completed = True
        preq.error = True
        inst.inbuf.append(b'GET / HTTP/1.1\n\n')
        inst.received()
        self.assertEqual(inst.request, None)
        self.assertEqual(len(inst.server.tasks), 1)
        self.assertTrue(inst.task)

    def test_received_preq_completed_connection_close(self):
        inst, sock, map = self._makeOneWithMap()
        inst.server = DummyServer()
        preq = DummyParser()
        inst.request = preq
        preq.completed = True
        preq.empty = True
        preq.connection_close = True
        inbuf = inst.inbuf
        inbuf.append(b'GET / HTTP/1.1\n\n' + b'a' * 50000)
        inst.received()
        self.assertEqual(inst.request, None)
        self.assertEqual(inst.server.tasks, [])
        self.assertNotEqual(inst.inbuf, inbuf)

    def test_received_preq_completed_n_lt_data(self):
        inst, sock, map = self._makeOneWithMap()
        inst.server = DummyServer()
        preq = DummyParser()
        inst.request = preq
        preq.completed = True
        preq.empty = True
        preq.retval = 1
        inst.inbuf.append(b'GET / HTTP/1.1\n\n')
        inst.received()
        self.assertEqual(inst.request, None)
        self.assertEqual(inst.task, None)
        self.assertEqual(inst.server.tasks, [])

    def test_received_headers_finished_not_expect_continue(self):
        inst, sock, map = self._makeOneWithMap()
        inst.server = DummyServer()
        preq = DummyParser()
        inst.request = preq
        preq.expect_continue = False
        preq.headers_finished = True
        preq.completed = False
        preq.empty = False
        preq.retval = 1
        inst.inbuf.append(b'GET / HTTP/1.1\n\n')
        inst.received()
        self.assertEqual(inst.request, preq)
        self.assertEqual(inst.server.tasks, [])
        self.assertEqual(inst.outbuf.get(100), b'')

    def test_received_headers_finished_expect_continue(self):
        inst, sock, map = self._makeOneWithMap()
        inst.server = DummyServer()
        preq = DummyParser()
        inst.request = preq
        preq.expect_continue = True
        preq.headers_finished = True
        preq.completed = False
        preq.empty = False
        preq.retval = 1
        inst.inbuf.append(b'GET / HTTP/1.1\n\n')
        inst.received()
        self.assertEqual(inst.request, preq)
        self.assertEqual(inst.server.tasks, [])
        self.assertEqual(inst.outbuf.get(100), b'HTTP/1.1 100 Continue\r\n\r\n')

    ## def test_handle_request(self):
    ##     req = DummyParser()
    ##     inst, sock, map = self._makeOneWithMap()
    ##     inst.server = DummyServer()
    ##     inst.handle_request(req)
    ##     self.assertEqual(inst.server.tasks, [inst])
    ##     self.assertEqual(len(inst.tasks), 1)
    ##     self.assertEqual(inst.tasks[0].__class__.__name__, 'WSGITask')

    ## def test_handle_request_error(self):
    ##     req = DummyParser()
    ##     req.error = True
    ##     inst, sock, map = self._makeOneWithMap()
    ##     inst.server = DummyServer()
    ##     inst.handle_request(req)
    ##     self.assertEqual(inst.server.tasks, [inst])
    ##     self.assertEqual(len(inst.tasks), 1)
    ##     self.assertEqual(inst.tasks[0].__class__.__name__, 'ErrorTask')

    def test_handle_error_reraises_SystemExit(self):
        inst, sock, map = self._makeOneWithMap()
        self.assertRaises(SystemExit,
                          inst.handle_error, (SystemExit, None, None))

    def test_handle_error_reraises_KeyboardInterrupt(self):
        inst, sock, map = self._makeOneWithMap()
        self.assertRaises(KeyboardInterrupt,
                          inst.handle_error, (KeyboardInterrupt, None, None))

    def test_handle_error_noreraise(self):
        inst, sock, map = self._makeOneWithMap()
        # compact_traceback throws an AssertionError without a traceback
        self.assertRaises(AssertionError, inst.handle_error,
                          (ValueError, ValueError('a'), None))

    def test_handle_comm_error_log(self):
        inst, sock, map = self._makeOneWithMap()
        inst.adj.log_socket_errors = True
        # compact_traceback throws an AssertionError without a traceback
        self.assertRaises(AssertionError, inst.handle_comm_error)

    def test_handle_comm_error_no(self):
        inst, sock, map = self._makeOneWithMap()
        inst.adj.log_socket_errors = False
        inst.handle_comm_error()
        self.assertEqual(inst.connected, False)
        self.assertEqual(sock.closed, True)

    ## def test_queue_task_no_existing_tasks_notrunning(self):
    ##     inst, sock, map = self._makeOneWithMap()
    ##     inst.server = DummyServer()
    ##     task = DummyTask()
    ##     inst.queue_task(task)
    ##     self.assertEqual(inst.tasks, [task])
    ##     self.assertTrue(inst.running_tasks)
    ##     self.assertFalse(inst.async_mode)
    ##     self.assertEqual(inst.server.tasks, [inst])

    ## def test_queue_task_no_existing_tasks_running(self):
    ##     inst, sock, map = self._makeOneWithMap()
    ##     inst.server = DummyServer()
    ##     inst.running_tasks = True
    ##     task = DummyTask()
    ##     inst.queue_task(task)
    ##     self.assertEqual(inst.tasks, [task])
    ##     self.assertTrue(inst.async_mode)

    def test_service_no_task(self):
        inst, sock, map = self._makeOneWithMap()
        inst.task = None
        inst.service()
        self.assertEqual(inst.task, None)

    def test_service_with_task(self):
        inst, sock, map = self._makeOneWithMap()
        task = DummyTask()
        inst.task = task
        inst.service()
        self.assertEqual(inst.task, None)
        self.assertTrue(task.serviced)

    def test_service_with_task_raises(self):
        inst, sock, map = self._makeOneWithMap()
        inst.adj.expose_tracebacks = False
        inst.server = DummyServer()
        task = DummyTask(ValueError)
        task.wrote_header = False
        inst.task = task
        inst.logger = DummyLogger()
        inst.service()
        self.assertTrue(task.serviced)
        self.assertEqual(inst.task, None)
        self.assertEqual(len(inst.logger.exceptions), 1)
        self.assertTrue(sock.sent)

    def test_service_with_task_raises_with_expose_tbs(self):
        inst, sock, map = self._makeOneWithMap()
        inst.adj.expose_tracebacks = True
        inst.server = DummyServer()
        task = DummyTask(ValueError)
        task.wrote_header = False
        inst.task = task
        inst.logger = DummyLogger()
        inst.service()
        self.assertTrue(task.serviced)
        self.assertEqual(inst.task, None)
        self.assertEqual(len(inst.logger.exceptions), 1)
        self.assertTrue(sock.sent)

    def test_service_with_task_raises_already_wrote_header(self):
        inst, sock, map = self._makeOneWithMap()
        inst.adj.expose_tracebacks = False
        inst.server = DummyServer()
        task = DummyTask(ValueError)
        task.wrote_header = True
        inst.task = task
        inst.logger = DummyLogger()
        inst.service()
        self.assertTrue(task.serviced)
        self.assertEqual(inst.task, None)
        self.assertEqual(len(inst.logger.exceptions), 1)
        self.assertFalse(sock.sent)

    def test_cancel_no_task(self):
        inst, sock, map = self._makeOneWithMap()
        inst.task = None
        inst.cancel()
        self.assertEqual(inst.task, None)

    def test_cancel_with_task(self):
        inst, sock, map = self._makeOneWithMap()
        task = DummyTask()
        inst.task = task
        inst.cancel()
        self.assertEqual(inst.task, None)
        self.assertEqual(task.cancelled, True)

    def test_defer(self):
        inst, sock, map = self._makeOneWithMap()
        self.assertEqual(inst.defer(), None)

class DummySock(object):
    blocking = False
    closed = False
    def __init__(self):
        self.sent = b''
    def setblocking(self, *arg):
        self.blocking = True
    def fileno(self):
        return 100
    def getpeername(self):
        return '127.0.0.1'
    def close(self):
        self.closed = True
    def send(self, data):
        self.sent += data
        return len(data)

class DummyBuffer(object):
    def __init__(self, data, toraise=None):
        self.data = data
        self.toraise = toraise

    def get(self, *arg):
        if self.toraise:
            raise self.toraise
        data = self.data
        self.data = b''
        return data

    def skip(self, num, x):
        self.skipped = num

class DummyAdjustments(object):
    outbuf_overflow = 1048576
    inbuf_overflow = 512000
    cleanup_interval = 900
    send_bytes = 9000
    url_scheme = 'http'
    channel_timeout = 300
    log_socket_errors = True
    recv_bytes = 8192
    expose_tracebacks = True
    ident = 'waitress'

class DummyServer(object):
    trigger_pulled = False
    adj = DummyAdjustments()
    def __init__(self):
        self.tasks = []
        self.active_channels = {}
    def add_task(self, task):
        self.tasks.append(task)
    def pull_trigger(self):
        self.trigger_pulled = True

class DummyParser(object):
    version = 1
    data = None
    completed = True
    empty = False
    headers_finished = False
    expect_continue = False
    retval = None
    error = None
    connection_close = False
    def received(self, data):
        self.data = data
        if self.retval is not None:
            return self.retval
        return len(data)

class DummyRequest(object):
    uri = 'http://example.com'
    
class DummyTask(object):
    serviced = False
    cancelled = False
    close_on_finish = False
    request = DummyRequest()
    wrote_header = False
    def __init__(self, toraise=None):
        self.toraise = toraise
    def service(self):
        self.serviced = True
        if self.toraise:
            raise self.toraise
    def cancel(self):
        self.cancelled = True

class DummyLogger(object):
    def __init__(self):
        self.exceptions = []
    def exception(self, msg):
        self.exceptions.append(msg)

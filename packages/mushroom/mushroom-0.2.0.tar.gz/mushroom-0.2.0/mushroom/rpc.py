from itertools import count
import logging

import gevent
from gevent.event import Event


logger = logging.getLogger('mushroom.rpc')


class RpcError(RuntimeError):
    pass


class MethodNotFound(RpcError):
    pass


class RequestTimeout(RpcError):
    pass


class RequestException(RpcError):

    def __init__(self, data):
        super(RequestException, self).__init__()
        self.data = data


class MethodDispatcher(object):

    def __init__(self, obj, prefix='rpc_'):
        self.obj = obj
        self.prefix = prefix

    def __call__(self, request):
        method_name = self.prefix + request.method
        try:
            method = getattr(self.obj, method_name)
        except AttributeError:
            raise MethodNotFound(method_name)
        return method(request)


def dummy_rpc_handler(request):
    '''
    Dummy RPC handler that raises a MethodNotFound exception for
    all calls. This is useful for applications that do not need do
    receive any data from the client but only publish data.
    '''
    raise MethodNotFound(request.method)


class Engine(object):
    '''Transport neutral message factory and mapper between requests and
    responses.'''

    def __init__(self, transport, rpc_handler):
        # Transport for sending and receiving messages
        self.transport = transport
        # Handler for inbound requests and notifications
        self.rpc_handler = rpc_handler
        # Generator for outbount message ids
        self.message_id_generator = count()
        # Dictionary for mapping outbound requests to inbound responses
        self.requests = {}
        # Greenlet for the receive main loop
        self.greenlet = None
        # Last message id received from the other side
        self.last_message_id = None

    def start(self):
        '''Start the receiver loop.'''
        assert self.greenlet is None
        self.greenlet = gevent.spawn(self.main)

    def stop(self):
        '''Stop the receiver loop.'''
        if self.greenlet:
            self.greenlet.kill()

    def main(self):
        '''Receive messages for all eternity or until the greenlet
        running this method is killed.'''
        while True:
            self.receive()

    def next_message_id(self):
        '''Generate the next message id for outbound messages.'''
        return self.message_id_generator.next()

    def notify(self, method, params=None, **kwargs):
        '''Send a notification.'''
        message = Notification(method, params, message_id=self.next_message_id())
        self.send(message, **kwargs)

    def request(self, method, params=None, timeout=None, **kwargs):
        '''Send a request and wait for the response or timeout.'''
        request = Request(method, params, message_id=self.next_message_id())
        self.requests[request.message_id] = request
        self.send(request, **kwargs)
        response = request.get_response(timeout)
        if isinstance(response, Response):
            return response.data
        elif isinstance(response, Error):
            raise RequestException(response.data)

    def send(self, message, **kwargs):
        '''Hand message over to the transport.'''
        self.transport.send(message, **kwargs)

    def receive(self):
        '''Get next message from the transport.'''
        message = self.transport.receive()
        '''
        if hasattr(message, 'message_id'):
            # Drop messages that we have already processed.
            message_id = message.message_id
            if message_id <= self.last_message_id:
                return
        '''
        if isinstance(message, Heartbeat):
            # FIXME Acknowledge messages from send queue. This
            #       requires a send queue first.
            pass
        elif isinstance(message, Notification):
            # Spawn worker to process the notification. The response of
            # the worker is ignored.
            gevent.spawn(self.rpc_handler, message)
        elif isinstance(message, Request):
            # Spawn worker which waits for the response of the rpc handler
            # and sends the response message.
            def worker(request):
                response = self.rpc_handler(request)
                self.send(response)
            gevent.spawn(worker, message)
        elif isinstance(message, (Response, Error)):
            # Find request according to response or error.
            try:
                request = self.requests.pop(message.request)
            except KeyError:
                logger.error('Response for unknown request message id: %r' %
                        message.request)
                return
            request.response = message
        elif isinstance(message, Disconnect):
            # FIXME how should this be handled? Maybe just a simple
            #       call to the rpc_handler?
            pass
        else:
            raise RuntimeError('Unsupported message type: %s' % type(message))


class Message(object):
    session = None

    @staticmethod
    def from_list(l, session=None):
        if not isinstance(l, (list, tuple)):
            raise ValueError('Message is not encoded as list or tuple')
        try:
            message_class = MESSAGE_CLASS_BY_CODE[l[0]]
        except KeyError:
            raise ValueError('Unsupported message code: %r' % l[0])
        message = message_class.from_list(l)
        message.session = session
        return message


class Heartbeat(Message):
    code = 0

    def __init__(self, last_message_id):
        self.last_message_id = last_message_id

    @staticmethod
    def from_list(l):
        self = Heartbeat(l[1])
        return self


class Notification(Message):
    code = 1
    message_id = None

    def __init__(self, method, data=None, message_id=None):
        self.method = method
        self.data = data
        self.message_id = message_id

    @staticmethod
    def from_list(l):
        self = Notification(l[2], l[3], message_id=l[1])
        return self

    def to_list(self):
        return [self.code, self.message_id, self.method, self.data]


class Request(Message):
    code = 2
    message_id = None

    def __init__(self, method, data=None, message_id=None):
        self.method = method
        self.data = data
        self.message_id = message_id
        self._response = None
        self.complete = Event()

    def to_list(self):
        return [self.code, self.message_id, self.method, self.data]

    @staticmethod
    def from_list(l):
        self = Request(l[2], l[3], message_id=l[1])
        return self

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, response):
        assert not self._response
        self._response = response
        self.complete.set()

    def get_response(self, timeout=None):
        if self.complete.wait(timeout):
            return self.response
        else:
            raise RequestTimeout

    def send_response(self, data):
        self.session.send(Response(self, data))

    def send_error(self, data):
        self.session.send(Error(self, data))


class Response(Message):
    code = 3
    message_id = None

    def __init__(self, request, data, message_id=None):
        self.request = request
        self.data = data
        self.message_id = message_id

    @staticmethod
    def from_list(l):
        self = Response(l[2], l[3], message_id=l[1])
        return self

    def to_list(self):
        return [self.code, self.message_id, self.request.message_id, self.data]


class Error(Message):
    code = 4
    message_id = None

    def __init__(self, request, data, message_id=None):
        self.request = request
        self.data = data
        self.message_id = message_id

    @staticmethod
    def from_list(l):
        self = Error(l[2], l[3], message_id=l[1])
        return self


class Disconnect(Message):
    code = -1

    @staticmethod
    def from_list(l):
        self = Disconnect()
        return self


MESSAGE_CLASS_BY_CODE = {
    Heartbeat.code: Heartbeat,
    Notification.code: Notification,
    Request.code: Request,
    Response.code: Response,
    Error.code: Error,
    Disconnect.code: Disconnect
}

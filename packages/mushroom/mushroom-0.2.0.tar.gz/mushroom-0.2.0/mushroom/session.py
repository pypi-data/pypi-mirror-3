from itertools import count
import random
import string
from time import time

import gevent
from gevent.event import Event
try:
    import simplejson as json
except ImportError:
    import json

from mushroom.http import JsonResponse
from mushroom.rpc import Message
from mushroom.rpc import Heartbeat
from mushroom.rpc import Request
from mushroom.rpc import Notification


POLL_TIMEOUT = 40
SESSION_CLEANUP_INTERVAL = 30
SESSION_MAX_AGE = 60


def session_id_generator():
    alpha_numerics = string.ascii_letters + string.digits
    while True:
        '''A UUID has 16 bytes and therefore 256^16 possibilities. For the
        shortest possible id which consists only of URL safe characters we
        pick only alpha numeric characters (2*26+10) and make it 22
        characters long. This is at least as good as a hex encoded UUID
        which would require 32 characters.'''
        yield ''.join(random.choice(alpha_numerics) for _ in xrange(22))


class Session(object):

    def __init__(self, id, rpc_handler):
        self.id = id
        self.rpc_handler = rpc_handler
        self.index = 0
        self.active = False
        self.last_activity = time()
        self.messages = []
        self.messages_ready = Event()
        self.message_id_generator = count()
        # This last message id variable is used for discarding
        # duplicate messages received from the client.
        self.last_message_id = None

    def send(self, message):
        if hasattr(message, 'message_id'):
            if message.message_id is not None:
                raise RuntimeError('The same message must not be sent twice.')
            message.message_id = self.message_id_generator.next()
        self.messages.append(message)
        self.messages_ready.set()

    def notify(self, method, data=None):
        self.send(Notification(method, data))

    def request(self, method, data, callback):
        raise NotImplementedError

    def next_index(self):
        self.index += 1
        return self.index

    def acknowledge(self, last_message_id):
        # Find index of first message that is not being acknowledged.
        index = 0
        for message in self.messages:
            if message.message_id <= last_message_id:
                index += 1
            else:
                break
        # Remove all acknowledged messages.
        if index > 0:
            self.messages = self.messages[index:]
        # Clear messages_ready event if there are no messages left.
        if not self.messages:
            self.messages_ready.clear()

    def get_messages(self, timeout=None, limit=None):
        self.active = True
        self.messages_ready.wait(timeout)
        self.active = False
        self.last_activity = time()
        if limit is None:
            return self.messages
        else:
            return self.messages[:limit]

    def handle_message(self, message):
        if hasattr(message, 'message_id'):
            if message.message_id < self.last_message_id:
                # skip messages that we have already processed
                return
            self.last_message_id = message.message_id
        if isinstance(message, Heartbeat):
            self.acknowledge(message.last_message_id)
        elif isinstance(message, Request):
            def worker(message):
                try:
                    response = self.rpc_handler(message)
                    # FIXME add support for RpcErrors
                except Exception, e:
                    message.send_error('Internal server error')
                    raise
                else:
                    message.send_response(response)
            gevent.spawn(worker, message)
        elif isinstance(message, Notification):
            gevent.spawn(self.rpc_handler, message)
        else:
            # XXX this should never be reached
            raise RuntimeError('Unsupported message type: %s' % type(message))

    def get_url(self, request, protocol):
        host = request.environ['HTTP_HOST']
        return '%s://%s/%s/' % (protocol, host, self.id)


class PollSession(Session):

    POLL_TIMEOUT = 40
    POLL_LIMIT = 100

    def get_handshake_data(self, request):
        protocol = 'http' # XXX autodetect
        return {
            'transport': 'poll',
            'url': self.get_url(request, protocol)
        }

    def handle_request(self, request):
        # Only allow POST requests for polling
        if request.method != 'POST':
            raise HttpMethodNotAllowed(['POST'])
        assert isinstance(request.data, list)
        heartbeat = None
        for message_data in request.data:
            message = Message.from_list(message_data, session=self)
            self.handle_message(message)
            if isinstance(message, Heartbeat):
                heartbeat = message
        if heartbeat:
            self.acknowledge(heartbeat.last_message_id)
            return JsonResponse([
                message.to_list()
                for message in self.get_messages(
                    timeout=PollSession.POLL_TIMEOUT,
                    limit=PollSession.POLL_LIMIT)
            ])
        else:
            return JsonResponse(None)


class WebSocketSession(Session):

    MAX_MESSAGE_SIZE = 64 * 1024 # 64 KiB

    def __init__(self, *args, **kwargs):
        super(WebSocketSession, self).__init__(*args, **kwargs)
        self.ws = None

    def get_handshake_data(self, request):
        protocol = 'ws' # XXX autodetect
        return {
            'transport': 'ws',
            'url': self.get_url(request, protocol)
        }

    def handle_request(self, request):
        self.ws = request.environ['wsgi.websocket']
        # Deliver messages which are already in the queue
        for message in self.get_messages(timeout=0):
            self.ws_send(message)
        # Process incoming messages
        while True:
            frame = self.ws.receive()
            if frame is None:
                # Disconnect
                # FIXME make sure the session is removed from the session list
                self.ws = None
                return
            message_data = json.loads(frame)
            message = Message.from_list(message_data, session=self)
            self.handle_message(message)

    def send(self, message):
        super(WebSocketSession, self).send(message)
        if self.ws:
            self.ws_send(message)

    def ws_send(self, message):
        message_data = message.to_list()
        frame = json.dumps(message_data)
        # FIXME this can fail if the websocket goes down
        self.ws.send(frame)


class SessionList(object):

    def __init__(self):
        self.sessions = {}

    def add(self, session):
        if session.id in self.sessions:
            raise KeyError('Duplicate session id %r' % session.id)
        self.sessions[session.id] = session

    def remove(self, session):
        del self.sessions[session.id]

    def notify(self, method, data=None):
        for session in self.sessions.itervalues():
            session.notify(method, data)

    def __getitem__(self, sid):
        return self.sessions[sid]

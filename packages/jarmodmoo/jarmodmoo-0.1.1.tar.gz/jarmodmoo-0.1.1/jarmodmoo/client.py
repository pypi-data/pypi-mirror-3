"""Majordomo Protocol Client API, Python version.

Implements the MDP/Worker spec at http:#rfc.zeromq.org/spec:7.

Author: Min RK <benjaminrk@gmail.com>
Based on Java example by Arkadiusz Orzechowski
"""

import logging

import zmq

from jarmodmoo.protocol import C_CLIENT
from jarmodmoo.config import HEARTBEAT_LIVENESS
from jarmodmoo.config import HEARTBEAT_INTERVAL
from jarmodmoo.config import CLIENT_CONNECT
from jarmodmoo.helpers import dump


class BaseClient(object):
    broker = None
    ctx = None
    client = None
    poller = None

    def __init__(self, broker=None, context=None):
        self.broker = broker or CLIENT_CONNECT
        self.ctx = context or zmq.Context()
        self.poller = zmq.Poller()
        self.logger = logging.getLogger('jarmodmoo.client')
        self.reconnect_to_broker()

    def reconnect_to_broker(self):
        """Connect or reconnect to broker"""
        if self.client:
            self.poller.unregister(self.client)
            self.client.close()
        self.client = self.ctx.socket(self._zmq_type)
        self.client.linger = 0
        self.client.connect(self.broker)
        self.poller.register(self.client, zmq.POLLIN)
        self.logger.info("connecting to broker at %s...", self.broker)

    def _send_multipart(self, service, request):
        assert isinstance(request, list)
        frames = []
        if self._req_emulation:
            frames.append('')
        frames.extend([C_CLIENT, service] + request)
        self.logger.debug("send request to '%s' service: \n%s", 
                         service, dump(frames))
        self.client.send_multipart(frames)

    def _get_multipart(self):
        msg = self.client.recv_multipart()
        self.logger.debug("received reply: \n%s", dump(msg))
        return self._get_validate_payload(msg)

    def _get_validate_payload(self, msg):
        # Don't try to handle errors, just assert noisily
        if self._req_emulation:
            assert len(msg) >= 4
            assert not msg.pop(0) # empty
        else:
            assert len(msg) >= 3
        assert C_CLIENT == msg.pop(0)
        msg.pop(0) # pop service
        return msg

    def destroy(self):
        self.ctx.destroy()


class SyncClient(BaseClient):
    """Majordomo Protocol Client API, Python version.

      Implements the MDP/Worker spec at http:#rfc.zeromq.org/spec:7.
    """
    _zmq_type = zmq.REQ
    _req_emulation = False
    
    def send(self, service, request):
        """Send request to broker and get reply by hook or crook.
        
        Takes ownership of request message and destroys it when sent.
        Returns the reply message or None if there was no reply.
        """
        reply = None
        retries = HEARTBEAT_LIVENESS
        while retries > 0:
            self._send_multipart(service, request)
            try:
                items = self.poller.poll(HEARTBEAT_INTERVAL)
            except KeyboardInterrupt:
                break # interrupted
            
            if items:
                reply = self._get_multipart()
                break
            else:
                if retries:
                    self.logger.warn("no reply, reconnecting...")
                    self.reconnect_to_broker()
                else:
                    self.logger.warn("permanent error, abandoning")
                    break
                retries -= 1
        
        return reply


class AsyncClient(BaseClient):
    """Majordomo Protocol Client API, Python version.

      Implements the MDP/Worker spec at http:#rfc.zeromq.org/spec:7.
    """
    _zmq_type = zmq.DEALER
    _req_emulation = True

    def send(self, service, request):
        """Send request to broker
        """
        self._send_multipart(service, request)

    def recv(self):
        """Returns the reply message or None if there was no reply."""
        try:
            items = self.poller.poll(HEARTBEAT_INTERVAL)
        except KeyboardInterrupt:
            return # interrupted
        
        if items:
            return self._get_multipart()
        else:
            self.logger.warn("permanent error, abandoning request")

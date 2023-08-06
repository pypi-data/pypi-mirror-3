"""Majordomo Protocol Worker API, Python version

Implements the MDP/Worker spec at http:#rfc.zeromq.org/spec:7.

Author: Min RK <benjaminrk@gmail.com>
Based on Java example by Arkadiusz Orzechowski
"""

import logging
import time
import zmq

from jarmodmoo.protocol import W_WORKER
from jarmodmoo.protocol import W_READY
from jarmodmoo.protocol import W_REQUEST
from jarmodmoo.protocol import W_REPLY
from jarmodmoo.protocol import W_HEARTBEAT
from jarmodmoo.protocol import W_DISCONNECT
from jarmodmoo.config import HEARTBEAT_INTERVAL
from jarmodmoo.config import HEARTBEAT_LIVENESS
from jarmodmoo.config import WORKER_CONNECT
from jarmodmoo.config import WORKER_RECONNECT_DELAY
from jarmodmoo.helpers import dump

class Worker(object):
    """Majordomo Protocol Worker API, Python version
    
    Implements the MDP/Worker spec at http:#rfc.zeromq.org/spec:7.
    """
    
    broker = None
    ctx = None
    service = None

    worker = None # Socket to broker
    heartbeat_at = 0 # When to send HEARTBEAT (relative to time.time(), so in seconds)
    liveness = 0 # How many attempts left
    
    # Internal state
    expect_reply = False # False only at start

    # Return address, if any
    reply_to = None
    
    def __init__(self, service, broker=None):
        self.service = service
        self.broker = broker or WORKER_CONNECT
        self.ctx = zmq.Context()
        self.poller = zmq.Poller()
        self.logger = logging.getLogger('jarmodmoo.worker')
        self.reconnect_to_broker()

    def reconnect_to_broker(self):
        """Connect or reconnect to broker"""
        if self.worker:
            self.poller.unregister(self.worker)
            self.worker.close()
        self.worker = self.ctx.socket(zmq.DEALER)
        self.worker.linger = 0
        self.worker.connect(self.broker)
        self.poller.register(self.worker, zmq.POLLIN)
        self.logger.info("connecting to broker at %s...", self.broker)
        
        # Register service with broker
        self.send_to_broker(W_READY, self.service, [])
        
        # If liveness hits zero, queue is considered disconnected
        self.liveness = HEARTBEAT_LIVENESS
        self.heartbeat_at = time.time() + 1e-3 * HEARTBEAT_INTERVAL

    def send_to_broker(self, command, option=None, msg=None):
        """Send message to broker.
        
        If no msg is provided, creates one internally
        """
        if msg is None:
            msg = []
        assert isinstance(msg, list)
        
        if option:
            msg = [option] + msg
        
        msg = ['', W_WORKER, command] + msg
        self.logger.debug("sending %s to broker: \n%s", command, dump(msg))
        self.worker.send_multipart(msg)
    
    def recv(self, reply=None):
        """Send reply, if any, to broker and wait for next request."""
        # Format and send the reply if we were provided one
        assert reply is not None or not self.expect_reply

        if reply is not None:
            assert self.reply_to is not None
            reply = [self.reply_to, ''] + reply
            self.send_to_broker(W_REPLY, msg=reply)
        
        self.expect_reply = True
        
        while True:
            # Poll socket for a reply, with timeout
            try:
                items = self.poller.poll(HEARTBEAT_INTERVAL)
            except KeyboardInterrupt:
                break # Interrupted
            
            if items:
                msg = self.worker.recv_multipart()
                self.logger.debug("received message from broker: \n%s", 
                                 dump(msg))
                
                self.liveness = HEARTBEAT_LIVENESS
                # Don't try to handle errors, just assert noisily
                assert len(msg) >= 3

                empty = msg.pop(0)
                assert empty == ''

                header = msg.pop(0)
                assert header == W_WORKER

                command = msg.pop(0)
                if command == W_REQUEST:
                    # We should pop and save as many addresses as there are
                    # up to a null part, but for now, just save one...
                    self.reply_to = msg.pop(0)
                    # pop empty
                    assert msg.pop(0) == ''
                    
                    return msg # We have a request to process
                elif command == W_HEARTBEAT:
                    # Do nothing for heartbeats
                    pass
                elif command == W_DISCONNECT:
                    self.reconnect_to_broker()
                else :
                    self.logger.error("invalid input message: \n%s", dump(msg))
            
            else:
                self.liveness -= 1
                if self.liveness == 0:
                    self.logger.warn("disconnected from broker - retrying...")
                    try:
                        time.sleep(1e-3*WORKER_RECONNECT_DELAY)
                    except KeyboardInterrupt:
                        break
                    self.reconnect_to_broker()
            
            # Send HEARTBEAT if it's time
            if time.time() > self.heartbeat_at:
                self.send_to_broker(W_HEARTBEAT)
                self.heartbeat_at = time.time() + 1e-3*HEARTBEAT_INTERVAL
        
        self.logger.warn("interrupt received, killing worker...")
        return None
    
    def destroy(self):
        # context.destroy depends on pyzmq >= 2.1.10
        self.ctx.destroy()

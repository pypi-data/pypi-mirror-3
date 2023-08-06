"""Majordomo Protocol broker.

A minimal implementation of http:#rfc.zeromq.org/spec:7 and spec:8

Author: Min RK <benjaminrk@gmail.com>
Based on Java example by Arkadiusz Orzechowski

Packaged by Simon Pantzare <simon+jarmodmoo@pewpewlabs.com>
"""

import logging
import sys
import time
from binascii import hexlify
import re

import zmq

from jarmodmoo.protocol import C_CLIENT
from jarmodmoo.protocol import W_WORKER
from jarmodmoo.protocol import W_READY
from jarmodmoo.protocol import W_REQUEST
from jarmodmoo.protocol import W_REPLY
from jarmodmoo.protocol import W_HEARTBEAT
from jarmodmoo.protocol import W_DISCONNECT
from jarmodmoo.config import INTERNAL_SERVICE_PREFIX
from jarmodmoo.config import INTERNAL_SERVICE_REGEX
from jarmodmoo.config import HEARTBEAT_INTERVAL
from jarmodmoo.config import HEARTBEAT_EXPIRY
from jarmodmoo.config import BROKER_BIND
from jarmodmoo.helpers import dump


class BrokerWorker(object):
    """a Worker, idle or active"""
    identity = None # hex Identity of worker
    address = None # Address to route to
    service = None # Owning service, if known
    expiry = None # expires at this point, unless heartbeat
    
    def __init__(self, identity, address, lifetime):
        self.identity = identity
        self.address = address
        self.expiry = time.time() + 1e-3*lifetime


class BrokerService(object):
    """a single Service"""
    name = None # Service name
    requests = None # List of client requests
    waiting = None # List of waiting workers
    
    def __init__(self, name):
        self.name = name
        self.requests = []
        self.waiting = []


class Broker(object):
    """
    Majordomo Protocol broker
    A minimal implementation of http:#rfc.zeromq.org/spec:7 and spec:8
    """

    # ---------------------------------------------------------------------

    ctx = None # Our context
    socket = None # Socket for clients & workers
    poller = None # our Poller

    heartbeat_at = None# When to send HEARTBEAT
    services = None # known services
    workers = None # known workers
    waiting = None # idle workers

    verbose = False # Print activity to stdout

    # ---------------------------------------------------------------------


    def __init__(self):
        """Initialize broker state."""
        self.services = {}
        self.workers = {}
        self.waiting = []
        self.heartbeat_at = time.time() + 1e-3*HEARTBEAT_INTERVAL
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.ROUTER)
        self.socket.linger = 0
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)
        self.logger = logging.getLogger('jarmodmoo.broker')

    # ---------------------------------------------------------------------

    def mediate(self):
        """Main broker work happens here"""
        self.logger.info("mediating... ")
        while True:
            try:
                items = self.poller.poll(HEARTBEAT_INTERVAL)
            except KeyboardInterrupt:
                break # Interrupted
            if items:
                msg = self.socket.recv_multipart()
                self.logger.debug("received message: \n%s", dump(msg))

                sender = msg.pop(0)
                empty = msg.pop(0)
                assert empty == ''
                header = msg.pop(0)

                if header == C_CLIENT:
                    self.process_client(sender, msg)
                elif header == W_WORKER:
                    self.process_worker(sender, msg)
                else:
                    self.logger.error("invalid message: \n%s", dump(msg))
                
            self.purge_workers()
            self.send_heartbeats()

    def destroy(self):
        """Disconnect all workers, destroy context."""
        while self.workers:
            self.delete_worker(self.workers[0], True)
        self.ctx.destroy(0)
    

    def process_client(self, sender, msg):
        """Process a request coming from a client."""
        assert len(msg) >= 2 # Service name + body
        service = msg.pop(0)
        # Set reply return address to client sender
        msg = [sender,''] + msg
        if service.startswith(INTERNAL_SERVICE_PREFIX):
            self.service_internal(service, msg)
        else:
            self.dispatch(self.require_service(service), msg)
    

    def process_worker(self, sender, msg):
        """Process message sent to us by a worker."""
        assert len(msg) >= 1 # At least, command

        command = msg.pop(0)
        
        worker_ready = hexlify(sender) in self.workers

        worker = self.require_worker(sender)

        if command == W_READY:
            assert len(msg) >= 1 # At least, a service name
            service = msg.pop(0)
            # Not first command in session or Reserved service name
            if worker_ready or service.startswith(INTERNAL_SERVICE_PREFIX):
                self.delete_worker(worker, True)
            else:
                # Attach worker to service and mark as idle
                worker.service = self.require_service(service)
                self.worker_waiting(worker)
        elif command == W_REPLY:
            if worker_ready:
                # Remove & save client return envelope and insert the
                # protocol header and service name, then rewrap envelope.
                client = msg.pop(0)
                empty = msg.pop(0) # ?
                msg = [client, '', C_CLIENT, worker.service.name] + msg
                self.socket.send_multipart(msg)
                self.worker_waiting(worker)
            else:
                self.delete_worker(worker, True)
        elif command == W_HEARTBEAT:
            if worker_ready:
                worker.expiry = time.time() + 1e-3*HEARTBEAT_EXPIRY
            else:
                self.delete_worker(worker, True)
        elif command == W_DISCONNECT:
            self.delete_worker(worker, False)
        else:
            self.logger.error("invalid message: \n%s", dump(msg))
    
    def delete_worker(self, worker, disconnect):
        """Deletes worker from all data structures, and deletes worker."""
        assert worker is not None
        if disconnect:
            self.send_to_worker(worker, W_DISCONNECT, None, None)
        
        if worker.service is not None:
            worker.service.waiting.remove(worker)
        self.workers.pop(worker.identity)
    
    def require_worker(self, address):
        """Finds the worker (creates if necessary)."""
        assert address is not None
        identity = hexlify(address)
        worker = self.workers.get(identity)
        if worker is None:
            worker = BrokerWorker(identity, address, HEARTBEAT_EXPIRY)
            self.workers[identity] = worker
            self.logger.info("registering new worker: %s", identity)
        
        return worker
    
    def require_service(self, name):
        """Locates the service (creates if necessary)."""
        assert name is not None
        service = self.services.get(name)
        if service is None:
            service = BrokerService(name)
            self.services[name] = service
        
        return service
    
    def bind(self):
        """Bind broker to endpoint, can call this multiple times. 
        
        We use a single socket for both clients and workers.
        """
        self.socket.bind(BROKER_BIND)
        self.logger.info("MDP broker/0.1.1 is active at %s", BROKER_BIND)
    
    def service_internal(self, service, msg):
        """Handle internal service according to 8/MMI specification"""
        match = INTERNAL_SERVICE_REGEX.match(service)
        assert match is not None, match
        service_call = match.group(1)
        returncode = "501"
        if service_call == "service":
            name = msg[-1]
            returncode = "200" if name in self.services else "400"
            msg[-1] = returncode
        elif service_call == "services":
            msg[-1] = ",".join(self.services.keys())
        elif service_call == "worker_count":
            worker_count = len(self.workers.values())
            msg[-1] = str(worker_count)

        # insert the protocol header and service name after the routing envelope ([client, ''])
        msg = msg[:2] + [C_CLIENT, service] + msg[2:]
        self.socket.send_multipart(msg)
    
    def send_heartbeats(self):
        """Send heartbeats to idle workers if it's time"""
        if time.time() > self.heartbeat_at:
            for worker in self.waiting:
                self.send_to_worker(worker, W_HEARTBEAT, None, None)
            
            self.heartbeat_at = time.time() + 1e-3*HEARTBEAT_INTERVAL
    
    def purge_workers(self):
        """Look for & kill expired workers. 
        
        Workers are oldest to most recent, so we stop at the first alive worker.
        """
        while self.waiting:
            w = self.waiting[0]
            if w.expiry < time.time():
                self.logger.info("deleting expired worker: %s", w.identity)
                self.delete_worker(w, False)
                self.waiting.pop(0)
            else:
                break
    
    def worker_waiting(self, worker):
        """This worker is now waiting for work."""
        # Queue to broker and service waiting lists
        self.waiting.append(worker)
        worker.service.waiting.append(worker)
        worker.expiry = time.time() + 1e-3*HEARTBEAT_EXPIRY
        self.dispatch(worker.service, None)
    
    def dispatch(self, service, msg):
        """Dispatch requests to waiting workers as possible"""
        assert (service is not None)
        if msg is not None:# Queue message if any
            service.requests.append(msg)
        self.purge_workers()
        while service.waiting and service.requests:
            msg = service.requests.pop(0)
            worker = service.waiting.pop(0)
            self.waiting.remove(worker)
            self.send_to_worker(worker, W_REQUEST, None, msg)
    
    def send_to_worker(self, worker, command, option, msg=None):
        """Send message to worker.
        
        If message is provided, sends that message.
        """
        
        if msg is None:
            msg = []
        assert isinstance(msg, list)

        # Stack routing and protocol envelopes to start of message
        # and routing envelope 
        if option is not None:
            msg = [option] + msg
        msg = [worker.address, '', W_WORKER, command] + msg
        self.logger.debug("sending %r to worker: \n%s", command, dump(msg))
        self.socket.send_multipart(msg)


def main():
    """create and start new broker"""
    logging.basicConfig(stream=sys.stderr)
    logger = logging.getLogger("jarmodmoo")
    verbose = '-v' in sys.argv
    if verbose:
        logger.setLevel(logging.INFO)
    broker = Broker()
    broker.bind()
    broker.mediate()


if __name__ == '__main__':
    main()

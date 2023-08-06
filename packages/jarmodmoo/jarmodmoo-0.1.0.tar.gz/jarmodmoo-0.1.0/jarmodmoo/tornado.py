import zmq
from zmq.eventloop.zmqstream import ZMQStream

from jarmodmoo.client import AsyncClient


class StreamHandler(object):

    def __init__(self, service, callback):
        self.service = service
        self.client = AsyncClient(context=zmq.Context.instance())
        self.stream = ZMQStream(self.client.client)
        self.stream.on_recv(self._handle_reply)
        self.callback = callback

    def send(self, request):
        self.client.send(self.service, request)

    def _handle_reply(self, msg):
        self.stream.close()
        self.callback(self.client._get_validate_payload(self.service, msg))


def send(service, request, callback):
    stream_handler = StreamHandler(service, callback)
    stream_handler.send(request)

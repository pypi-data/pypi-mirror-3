from struct import unpack, pack
import logging

import zokket

from dnstk.packet import Packet, ResourceRecord
from dnstk.resources import *

logger = logging.getLogger(__name__)

class DNSServer(object):
    def __init__(self):
        zokket.TCPSocket(self).accept(port=53)
        zokket.UDPSocket(self).bind(port=53)

    def socket_will_connect(self, sock):
        sock.buffer_type = None
        sock.read_until_length = 2
        return True

    def socket_read_data(self, sock, data):
        if sock.read_until_length == 2:
            sock.read_until_length = unpack('>H', data)[0]
        else:
            payload = self.handle_dns_payload(sock, sock.connected_host(), data)
            sock.send(pack('>H', len(payload)))
            sock.send(payload)
            sock.read_until_length = 2

    def udp_socket_read_data(self, sock, host, port, data):
        payload = self.handle_dns_payload(sock, host, data)
        sock.send(host, port, payload)

    def handle_dns_payload(self, sock, host, payload):
        try:
            request = Packet.parse(payload)
        except Exception as e:
            request = None
            logger.error('Unable to parse packet: ' + e)

        if request:
            request.sock = sock
            request.host = host
            return self.handle_dns_packet(request)

    def handle_dns_packet(self, request):
        response = Packet(request.txid, request.flags)
        response.is_response = True
        response.rcode = 0
        response.questions = request.questions

        for question in request.questions:
            self.handle_dns_question(request, response, question)

        return bytes(response)

    def handle_dns_question(self, request, response, question):
        for letter in range(97, 110):
            name = chr(letter) + '.root-servers.net'
            response.authorities.append(ResourceRecord(resource=NSResource(name)))


def main():
    DNSServer()
    zokket.DefaultRunloop.run()

if __name__ == '__main__':
    main()


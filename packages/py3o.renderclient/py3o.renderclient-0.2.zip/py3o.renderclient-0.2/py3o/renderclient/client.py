from twisted.internet import reactor

from pyf.transport.packets import Packet
from pyf.station.client import StationClient

from pyf.station.utils import (base64encoder, base64decoder, file_to_packets,
        packets_to_file, handle_data_packet)

import logging

class RenderClient(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.authtkt = ''

    def login(self, user_name, password):
        self.authtkt = ''

    def render(self, input_filename, output_filename, target_format='pdf'):
        client = StationClient(self.host, self.port, waits_for_success=True)
        flow = base64encoder(file_to_packets(open(input_filename, 'rb')))

        values = base64decoder(client.call(
             flow,
             header=dict(authtkt=self.authtkt,
                         action='render',
                         target_format=target_format)))

        output_file = None
        i = 0
        while True:
            try:
                value = values.next()
            except StopIteration:
                break

            if isinstance(value, Packet) and value.type == 'appinfo' and value.key == 'render_status':
                if value.value == 'ok':
                    logging.info("Render of %s executed successfully. Trying to get output file." % input_filename)
                else:
                    raise ValueError, "Render failed, no reason given."

            if isinstance(value, Packet) and value.type == 'datatransfer':
                if output_file is None:
                    output_file = open(output_filename, 'wb')

                if handle_data_packet(value, output_file):
                    output_file.close()
                    logging.info("File %s written successfully" % output_filename)

            i+=1


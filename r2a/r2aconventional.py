import time

from player.parser import *
from r2a.ir2a import IR2A


class R2ARandom(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.parsed_mpd = None
        self.request_time_start = 0
        self.request_time_end = 0
        self.measured_throughputs = []
        self.qi = []

    def handle_xml_request(self, msg):
        self.send_down(msg)

    def handle_xml_response(self, msg):
        # getting qi list
        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()

        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        self.request_time_start = time.perf_counter()
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        self.request_time_end = time.perf_counter()
        rtt = self.request_time_end - self.request_time_start
        dt = rtt / 2
        # x do artigo
        throughput = msg.get_bit_length() / dt # ?
        self.measured_throughputs.append(throughput)
        self.send_up(msg)

    def initialize(self):
        # self.send_up(Message(MessageKind.SEGMENT_REQUEST, 'Olá Mundo'))
        pass

    def finalization(self):
        pass

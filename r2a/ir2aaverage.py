# -*- coding: utf-8 -*-
"""
@author: Marcos F. Caetano (mfcaetano@unb.br) 03/11/2020

@description: PyDash Project

Example from video.
"""

import time
import subprocess
from player.parser import *
from r2a.ir2a import IR2A

class IR2AAverage(IR2A):

    def __init__(self, id):
      IR2A.__init__(self, id)
      self.throughputs = []
      self.parsed_mpd = None
      self.qi = []
      self.request_time = 0
      pass

    def handle_xml_request(self, msg):
        self.request_time = time.time()        

        self.send_down(msg)
        pass

    def handle_xml_response(self, msg):
        print('>>>>>>>>>>>>>>>>>>>>')


        parsed_mpd = parse_mpd(msg.get_payload())
        # print(parsed_mpd.get_mpd_info())
        # print(parsed_mpd.get_period_info())
        print(parsed_mpd.get_qi())
        self.qi = parsed_mpd.get_qi()

        dt = time.time() - self.request_time
        print(f'>>> tempo passado:{dt}')

        throughput = msg.get_bit_length()/dt
        print('')
        print(f'>>> throughput :{throughput}')
        print('')

        self.throughputs.append(throughput)
        
        self.send_up(msg)
        pass

    def handle_segment_size_request(self, msg):
        msg.add_quality_id(self.qi[0])

        self.send_down(msg)
        pass

    def handle_segment_size_response(self, msg):
        print('>>>>>>>>>>>>>>>>>>>>>\n')
        print('bit len:', msg.get_bit_length())
        print('seg size:', msg.get_segment_size())
        print('>>>>>>>>>>>>>>>>>>>>>\n')

        self.send_up(msg)
        pass

    def initialize(self):
        pass

    def finalization(self):
        # seria interessante fazer um som para avisar que terminou
        subprocess.Popen(['notify-send', 'TESTE pyDASH TERMINOU'])
        pass

# -*- coding: utf-8 -*-
'''
r2adynamicsss: Rate Adaptation Algorithm, Dynamic Segment Size Selection
'''

import time
from player.parser import *
from r2a.ir2a import IR2A

class R2ADynamicSegmentSizeSelection(IR2A):
    def __init__(self, id):
        super().__init__(id)
        self.parsed_mpd = ''
        self.__WINDOW_SIZE = 50
        self.request_time = 0
        self.qi = []
        self.throughputs = MovingAverage(self.__WINDOW_SIZE)


    def handle_xml_request(self, msg):
        self.request_time = time.perf_counter()
        self.send_down(msg)


    def handle_xml_response(self, msg):
        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()

        time_passed = time.perf_counter() - self.request_time

        throughput = msg.get_bit_length() / (time_passed/2.0)

        self.throughputs.add_sample(throughput)
        
        self.send_up(msg)


    def handle_segment_size_request(self, msg):
        self.request_time = time.perf_counter()

        # time to define the segment quality choose to make the request
        msg.add_quality_id(self.qi[0])
        self.send_down(msg)


    def handle_segment_size_response(self, msg):
        time_passed = time.perf_counter() - self.request_time

        throughput = msg.get_bit_length() / (time_passed/2.0)

        self.throughputs.add_sample(throughput)

        print('>>>>>>>>>>>>>>>>>>>>>')
        print('bit len:', msg.get_bit_length())
        print('seg size:', msg.get_segment_size())
        print('>>>>>>>>>>>>>>>>>>>>>\n')

        self.send_up(msg)


    def initialize(self):
        pass


    def finalization(self):
        print('>>>>>>>>>>>>>>>>>>>>>\n')
        print(self.whiteboard.get_playback_qi())
        pass


'''
Classe para calcular as médias móveis de tamanho window_size. Amostras mais 
antigas possuem índices menores. Amostras mais recentes possuem índices maiores 
e entram no fim da lista com .append()

ex:
__samples = [mais antigo, mais recente, mais recente ainda]
'''
class MovingAverage:
    def __init__(self, window_size):
        # No artigo é M
        self.__WINDOW_SIZE = window_size
        self.__samples = []
    
    
    def add_sample(self, sample):
        is_a_number = isinstance(sample, int) or isinstance(sample, float)
        if not is_a_number:
            raise Exception('sample deve ser um número')

        current_size = len(self.__samples)
        
        reached_max_capacity = current_size >= self.__WINDOW_SIZE
        if reached_max_capacity:
            self.__remove_oldest_sample()
        
        self.__samples.append(sample)


    def get_average(self):
        avg = sum(self.__samples)/len(self.__samples)
        return avg


    def get_samples_size(self):
        return len(self.__samples)


    def get_sigma_weight_squared(self):
        avg = self.get_average()
        total = 0
        for i, sample in enumerate(self.__samples):
            total += (i+1.0)/self.__WINDOW_SIZE*abs(sample - avg)
        return total

    # Essas funções não são úteis ainda
    # def get_oldest_sample(self):
    #     return self.__samples[0]
    

    # def get_newest_sample(self):
    #     return self.__samples[-1]
    

    def __remove_oldest_sample(self):
        self.__samples.pop(0)

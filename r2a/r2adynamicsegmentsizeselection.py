# -*- coding: utf-8 -*-
'''
r2adynamicsss: Rate Adaptation Algorithm, Dynamic Segment Size Selection
'''
import subprocess
import time

from player.parser import *
from r2a.ir2a import IR2A

class R2ADynamicSegmentSizeSelection(IR2A):
    def __init__(self, id):
        super().__init__(id)
        self.parsed_mpd = ''
        self.__WINDOW_SIZE = 10
        self.request_time = 0
        self.qi = []
        self.throughputs = SlidingWindow(self.__WINDOW_SIZE)
        self.last_quality_index = 0


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
        # msg.add_quality_id(self.qi[0])
        # msg.add_quality_id(self.qi[self.last_quality_index])
        # GAMBIARRA
        msg.add_quality_id(self.qi[self.last_quality_index])
        self.send_down(msg)


    def handle_segment_size_response(self, msg):
        time_passed = time.perf_counter() - self.request_time

        throughput = msg.get_bit_length() / (time_passed/2.0)

        self.throughputs.add_sample(throughput)

        # new_qi = self.get_new_qi(self.last_quality_index)
        new_qi = min(self.get_new_qi(self.last_quality_index), 19)
        self.last_quality_index = new_qi #min(self.get_new_qi(self.last_quality_index), 19)
        last_qi = self.last_quality_index

        print('\n>>>>>>>>>>>>>>>>>>>>>')
        print('samples:', list(map(int, self.throughputs.get_samples())))
        print('u:', round(self.throughputs.get_average(), 2))
        print('σ:', round(self.throughputs.get_sigma_weight_squared(), 2))
        print('p:', round(self.throughputs.get_willingness_to_change(), 2))
        print('θ:', round(self.get_willingness_to_increase(last_qi), 2))
        print('τ:', round(self.get_willingness_to_decrease(last_qi), 2))
        print('new_qi:', new_qi)
        print('qi:', self.qi)
        print('>>>>>>>>>>>>>>>>>>>>>\n')

        
        self.send_up(msg)

    
    def get_new_qi(self, last_qi: int) -> int:
        will_to_inc = self.get_willingness_to_increase(last_qi)
        will_to_dec = self.get_willingness_to_decrease(last_qi)
        # como usa argmin aqui?
        # por algum motivo new_qi pode ficar maior que 20
        # ficar mexendo com os índices das qualidades dificulta um pouco
        new_qi = (last_qi - will_to_dec + will_to_inc)
        print('>>>>>>>>>>>>>>>>>>>>>>>|| new_qi', round(new_qi, 0))
        return int(round(new_qi, 0))


    def argmin(self, quality) -> int:
        # procurar dentro de self.qi o índice mais próximo para quality
        # retonar o índice
        return 0
    
    # 
    def get_willingness_to_decrease(self, last_qi) -> float:
        will_to_change = self.throughputs.get_willingness_to_change()
        # tentativa de retornar a qualidade
        # qi_to_decrease = max(0, last_qi-1)
        # will_to_dec = (1. - will_to_change)*self.qi[qi_to_decrease]
        ##########################################################
        will_to_dec = (1. - will_to_change)*max(0, last_qi-1)
        return will_to_dec


    # incompleto
    def get_willingness_to_increase(self, last_qi) -> float:
        will_to_change = self.throughputs.get_willingness_to_change()
        will_to_inc = will_to_change*min(20, last_qi+1)
        return will_to_inc


    def initialize(self):
        pass


    def finalization(self):
        print('>>>>>>>>>>>>>>>>>>>>>\n')
        subprocess.Popen(['notify-send',  'PYDASH TERMINOU'])
        # print(self.whiteboard.get_playback_qi())
        pass
    


'''Classe para calcular as médias móveis de tamanho window_size. Amostras mais 
antigas possuem índices menores. Amostras mais recentes possuem índices maiores 
e entram no fim da lista com .append()

ex:
__samples = [mais antigo, mais recente, mais recente ainda]'''
class SlidingWindow:
    def __init__(self, window_size):
        if (window_size <= 0):
            raise Exception('o tamanho da janela deve ser um inteiro positivo')
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


    def get_average(self) -> float:
        avg = sum(self.__samples)/len(self.__samples)
        return avg


    def get_samples_size(self) -> int:
        return len(self.__samples)


    def get_samples(self):
        return self.__samples.copy()


    def get_sigma_weight_squared(self) -> float:
        avg = self.get_average()
        current_len = len(self.__samples)
        sigma = 0
        for i, sample in enumerate(self.__samples):
            sigma += (i+1.0)/current_len*abs(sample - avg)
        return sigma


    def get_willingness_to_change(self) -> float: 
        avg = self.get_average()
        sigma_weight_squared = self.get_sigma_weight_squared()
        p = avg / (avg + sigma_weight_squared)
        return p
    

    def __remove_oldest_sample(self):
        self.__samples.pop(0)

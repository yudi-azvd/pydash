import unittest

from r2a.r2adynamicsegmentsizeselection import MovingAverage

class TestR2ADynamicSegmentSizeSelection(unittest.TestCase):

    def test_add_one_sample(self):
        moving_avg = MovingAverage(20)
        moving_avg.add_sample(10)
        avg = moving_avg.get_average()

        self.assertEqual(avg, 10)


    def test_add_two_samples(self):
        moving_avg = MovingAverage(20)
        moving_avg.add_sample(10)
        moving_avg.add_sample(10)
        avg = moving_avg.get_average()

        self.assertEqual(avg, 10)


    def test_add_40_samples(self):
        window_size = 5
        samples = 10
        moving_avg = MovingAverage(window_size)
        
        # 0, 1, 2, ..., 8, 9
        for sample in range(samples):
            moving_avg.add_sample(sample)
        
        # __samples em moving_avg: 5, 6, 7, 8, 9
        # sum(__samples): 35 => 35 / window_size: 7
        avg = moving_avg.get_average() 
        self.assertEqual(avg, 7)
    

    def test_get_window_size(self):
        window_size = 10
        moving_avg = MovingAverage(window_size)
        self.assertEqual(moving_avg.get_samples_size(), 0)

        moving_avg.add_sample(0)
        self.assertEqual(moving_avg.get_samples_size(), 1)
        moving_avg.add_sample(0)
        self.assertEqual(moving_avg.get_samples_size(), 2)

        for _ in range(13):
            moving_avg.add_sample(0)

        self.assertEqual(moving_avg.get_samples_size(), 10, 'o tamanho da janela \
            não deve passar de 10, que é o tamanho máximo')
    

    # def test_get_oldest_sample(self):
    #     window_size = 10
    #     moving_avg = MovingAverage(window_size)

    #     oldest = moving_avg.get_oldest_sample()

    #     self.assertEqual(oldest, None)



if __name__ == '__main__':
    unittest.main()


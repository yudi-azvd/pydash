import unittest

from r2a.r2adynamicsegmentsizeselection import SlidingWindow

class TestR2ADynamicSegmentSizeSelection(unittest.TestCase):
    def test_add_one_sample(self):
        sliding_window = SlidingWindow(20)
        sliding_window.add_sample(10)
        avg = sliding_window.get_average()

        self.assertEqual(avg, 10)


    def test_add_two_samples(self):
        sliding_window = SlidingWindow(20)
        sliding_window.add_sample(10)
        sliding_window.add_sample(10)
        avg = sliding_window.get_average()

        self.assertEqual(avg, 10)


    def test_add_40_samples(self):
        window_size = 5
        samples = 10
        sliding_window = SlidingWindow(window_size)
        
        # 0, 1, 2, ..., 8, 9
        for sample in range(samples):
            sliding_window.add_sample(sample)
        
        # __samples em sliding_window: 5, 6, 7, 8, 9
        # sum(__samples): 35 => 35 / window_size: 7
        avg = sliding_window.get_average() 
        self.assertEqual(avg, 7)
    

    def test_get_window_size(self):
        window_size = 10
        sliding_window = SlidingWindow(window_size)
        self.assertEqual(sliding_window.get_samples_size(), 0)

        sliding_window.add_sample(0)
        self.assertEqual(sliding_window.get_samples_size(), 1)
        sliding_window.add_sample(0)
        self.assertEqual(sliding_window.get_samples_size(), 2)

        for _ in range(13):
            sliding_window.add_sample(0)

        self.assertEqual(sliding_window.get_samples_size(), 10, 'o tamanho da  \
            janela não deve passar de 10, que é o tamanho máximo')
    

    def test_get_sigma_wheight_squared(self):
        window_size = 5
        sliding_window = SlidingWindow(window_size)
        self.add_samples([20, 13, 14, 18, 7], sliding_window)

        sigma = sliding_window.get_sigma_weight_squared()

        self.assertAlmostEqual(sigma, 12.2)

    
    def test_willingness_to_change(self):
        window_size = 5
        sliding_window = SlidingWindow(window_size)
        self.add_samples([20, 13, 14, 18, 7], sliding_window)

        willingness = sliding_window.get_willingness_to_change()

        self.assertAlmostEqual(willingness, 0.541353383)


    def test_stable_samples(self):
        window_size = 5
        sliding_window = SlidingWindow(window_size)
        self.add_samples([20, 20, 20, 20, 20], sliding_window)

        willingness = sliding_window.get_willingness_to_change()

        self.assertAlmostEqual(willingness, 1.0)


    def test_unstable_samples(self):
        window_size = 5
        sliding_window = SlidingWindow(window_size)
        self.add_samples([20, 1000, 2, 500, 90], sliding_window)

        willingness = sliding_window.get_willingness_to_change()

        self.assertAlmostEqual(willingness, 0.26412373)


    def add_samples(self, samples, sliding_window: SlidingWindow):
        for sample in samples:
            sliding_window.add_sample(sample)


if __name__ == '__main__':
    unittest.main()


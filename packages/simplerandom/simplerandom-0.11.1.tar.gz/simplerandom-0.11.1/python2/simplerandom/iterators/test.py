"""
Simple random

Unit Tests
"""

import random
import unittest

import simplerandom.iterators as sri
#import simplerandom.iterators._iterators_py as sri


class Marsaglia1999Tests(unittest.TestCase):
    """Tests as in Marsaglia 1999 post
    
    The Marsaglia 1999 post didn't explicitly set seed values for each RNG,
    but relied on the seed values that were side-effects of previous RNG
    executions. But we want to run each test as a stand-alone unit. So we
    have obtained the seed values from the C execution, and set them
    explicitly in each test here.
    """

    def test_kiss_million(self):
        random_kiss = sri.KISS(2247183469, 99545079, 3269400377, 3950144837)
        for i in range(1000000):
            k = random_kiss.next()
        self.assertEqual(k, 2100752872)

    def test_cong_million(self):
        cong = sri.Cong(2051391225)
        for i in range(1000000):
            k = cong.next()
        self.assertEqual(k, 2416584377)

    def test_shr3_million(self):
        shr3 = sri.SHR3(3360276411)
        for i in range(1000000):
            k = shr3.next()
        self.assertEqual(k, 1153302609)

    def test_mwc1_million(self):
        mwc = sri.MWC1(2374144069, 1046675282)
        for i in range(1000000):
            k = mwc.next()
        self.assertEqual(k, 904977562)


class CongTest(unittest.TestCase):
    RNG_CLASS = sri.Cong
    RNG_SEEDS = 1
    RNG_BITS = 32
    RNG_RANGE = (1 << RNG_BITS)


    def setUp(self):
        # Make some random seed values
        self.rng_seeds = [ random.randrange(self.RNG_RANGE) for _i in range(self.RNG_SEEDS) ]

        # Make the RNG instance
        self.rng = self.RNG_CLASS(*self.rng_seeds)

    def test_seed(self):
        # Record its initial state
        state_from_init = self.rng.getstate()
        # Use the RNG to make some random numbers
        num_next_calls = random.randrange(3, 10)
        data_from_init = tuple([ self.rng.next() for _i in range(num_next_calls) ])
        # Get its state again
        state_after_data_from_init = self.rng.getstate()

        # Use the seed function to set its state to the same as before
        self.rng.seed(*self.rng_seeds)
        # Get its state again. It should be the same as before.
        state_from_seed = self.rng.getstate()
        self.assertEqual(state_from_init, state_from_seed)
        # Get random numbers again. They should be the same as before.
        data_from_seed = tuple([ self.rng.next() for _i in range(num_next_calls) ])
        self.assertEqual(data_from_init, data_from_seed)
        # Get its state again. It should be the same as before.
        state_after_data_from_seed = self.rng.getstate()
        self.assertEqual(state_after_data_from_init, state_after_data_from_seed)

    def test_state(self):
        # Run it for some random count
        count1 = random.randrange(100,1000)
        for _i in range(count1):
            self.rng.next()

        # Get the state
        rng_state = self.rng.getstate()

        # Run it again for a while
        count2 = 1000
        rng_data = [ self.rng.next() for _i in range(count2) ]

        # Now reset to the previous state, and re-run the data
        self.rng.setstate(rng_state)
        for i in range(count2):
            self.assertEqual(self.rng.next(), rng_data[i])

    def test_iter(self):
        """Test that __iter__ member function is present"""
        iter_object = iter(self.rng)


class SHR3Test(CongTest):
    RNG_CLASS = sri.SHR3


class MWC1Test(CongTest):
    RNG_CLASS = sri.MWC1
    RNG_SEEDS = 2


class KISS2Test(CongTest):
    RNG_CLASS = sri.KISS2
    RNG_SEEDS = 4
    MILLION_RESULT = 4044786495

    def test_million(self):
        rng = self.RNG_CLASS()
        for i in range(1000000):
            k = rng.next()
        self.assertEqual(k, self.MILLION_RESULT)


class MWC2Test(KISS2Test):
    RNG_CLASS = sri.MWC2
    RNG_SEEDS = 2
    MILLION_RESULT = 767834450

class MWC64Test(KISS2Test):
    RNG_CLASS = sri.MWC64
    RNG_SEEDS = 2
    MILLION_RESULT = 2191957470

    def test_seed_with_MSbit_set(self):
        """Test MWC64 with MS-bit of mwc_c seed set.
        
        This caused an exception in an earlier version of the Cython code
        (0.7.0) when built with Cython 0.14.
        """
        mwc64 = sri.MWC64(2**31, 1)
        mwc64.next()


class KISSTest(CongTest):
    RNG_CLASS = sri.KISS
    RNG_SEEDS = 4


class LFSR113Test(KISS2Test):
    RNG_CLASS = sri.LFSR113
    RNG_SEEDS = 4
    MILLION_RESULT = 300959510


class LFSR88Test(KISS2Test):
    RNG_CLASS = sri.LFSR88
    RNG_SEEDS = 3
    MILLION_RESULT = 3774296834


def runtests():
    unittest.main()


if __name__ == '__main__':
    runtests()


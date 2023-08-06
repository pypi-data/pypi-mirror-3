from tate_bilinear_pairing import f3
import unittest

class TestF3(unittest.TestCase):
    def testadd(self):
        for a, b, c in (
                        [0, 0, 0],
                        [0, 1, 1],
                        [0, 2, 2],
                        [1, 0, 1],
                        [1, 1, 2],
                        [1, 2, 0],
                        [2, 0, 2],
                        [2, 1, 0],
                        [2, 2, 1],
                        ):
            assert f3.add(a, b) == c

    def testneg(self):
        for a, b in (
                     [0, 0],
                     [1, 2],
                     [2, 1],
                     ):
            assert f3.neg(a) == b
    
    def testsub(self):
        for a, b, c in (
                        [0, 0, 0],
                        [0, 1, 2],
                        [0, 2, 1],
                        [1, 0, 1],
                        [1, 1, 0],
                        [1, 2, 2],
                        [2, 0, 2],
                        [2, 1, 1],
                        [2, 2, 0],
                        ):
            assert f3.sub(a, b) == c

    def testmult(self):
        for a, b, c in (
                        [0, 0, 0],
                        [0, 1, 0],
                        [0, 2, 0],
                        [1, 0, 0],
                        [1, 1, 1],
                        [1, 2, 2],
                        [2, 0, 0],
                        [2, 1, 2],
                        [2, 2, 1],
                        ):
            assert f3.mult(a, b) == c

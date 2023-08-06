from tate_bilinear_pairing import f32m
import unittest

class Test(unittest.TestCase):
    def test_mult(self):
        # the square of (x^4*s+x^4+2*x^2+2*x+1) is (x^4+2*x^3+x^2+1)*s+2*x^3+2*x^2+2*x+1, mod x^5+x^4+2
        f32m.f3m.m = 5
        a1 = [[1,2,2,0,1], [0,0,0,0,1]]
        a2 = [[1,2,2,0,1], [0,0,0,0,1]]
        b = [[1,2,2,2,0], [1,0,1,2,1]]
        self.assertEqual(f32m.mult(a1, a2), b)


from tate_bilinear_pairing import f3m
import unittest

class Test(unittest.TestCase):
    def test_add(self):
        a = f3m.E()
        a[1] = 1
        b = f3m.E()
        b[3] = 1
        f3m.add(a, b, a)
        assert a[:4] == [0, 1, 0, 1]

    def test_neg(self):
        a = f3m.E()
        a[1] = 1
        f3m.neg(a, a)
        self.assertEqual(a[:2], [0, 2])

    def test_sub(self):
        a = f3m.E()
        a[0] = 2
        b = f3m.E()
        b[1] = 1
        f3m.sub(a, b, a)
        assert a[:2] == [2, 2]

    def test_number_mult_poly(self):
        f3m.m = 4
        a = f3m.E()
        a[1] = 1
        a[3] = 2
        f3m._f1(2, a, a)
        assert a[:4] == [0, 2, 0, 1]

    def test_mult(self):
        f3m.m = 2
        a = f3m.E([0,1])
        b = f3m.E([0,1])
        self.assertEqual(f3m.mult(a, b), [1,2])
        
        a = f3m.E([1,1])
        b = f3m.E([0,1])
        self.assertEqual(f3m.mult(a, b), [1,0])
        
    def test_cubic(self):
        f3m.m = 5
        a = f3m.E([0,1,1,2,1])
        b = f3m.cubic(a)
        assert b[:5] == [0,1,2,0,1]
        
    def test_reduct(self):
        f3m.m = 4
        a = f3m.E([0, 0, 2, 1, 2])
        f3m.reduct(a)
        self.assertEqual(a, [2, 1, 2, 1])

    def test_inverse(self):
        f3m.m = 4
        a_list = ([1,1], [1,1,1], [1,1,1,1], [1], [2],)
        a_inv_list = ([0,1,2,1], [1,0,1,2], [0,0,0,1], [1], [2],)
        for a, a_inv in zip(a_list, a_inv_list):
            a1 = f3m.inverse(a)
            a2 = f3m.E(a_inv)
            self.assertEqual(a1, a2)


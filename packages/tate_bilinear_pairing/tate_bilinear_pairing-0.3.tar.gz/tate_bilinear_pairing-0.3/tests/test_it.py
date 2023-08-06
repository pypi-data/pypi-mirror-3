from tate_bilinear_pairing import it
import unittest

class Test(unittest.TestCase):
    def test1(self):
        'test non-existing irreducible trinomials'
        for m in list(range(256, 1024)) + [0, 1, 10, 34, 38, 49, 50, 57, 58, 62, 65, 66, 68, 70, 74, 75]:
            self.assertNotIn(m, it.table)

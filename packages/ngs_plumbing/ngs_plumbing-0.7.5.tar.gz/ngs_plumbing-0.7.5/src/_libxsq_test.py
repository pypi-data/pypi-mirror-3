import unittest
import io
import ngs_plumbing._libxsq as _libxsq

class LibxsqTestCase(unittest.TestCase):
    
    def test_colourqual_frombytes(self):
        self.assertRaises(TypeError, _libxsq.colourqual_frombytes, 10)
        bt = b'AC$##HBD^%A'
        col,qual = _libxsq.colourqual_frombytes(bt)

    def test_colourqual_frombytearray(self):
        self.assertRaises(TypeError, _libxsq.colourqual_frombytearray, 10)
        ba = bytearray(10)
        col,qual = _libxsq.colourqual_frombytearray(ba)

    def test_colourqual_frombuffer(self):
        self.assertRaises(TypeError, _libxsq.colourqual_frombuffer, 10)
        ba = bytearray(10)
        col,qual = _libxsq.colourqual_frombuffer(memoryview(ba))


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(LibxsqTestCase)
    return suite


def main():
    r = unittest.TestResult()
    suite().run(r)
    return r

if __name__ == "__main__":
    tr = unittest.TextTestRunner(verbosity = 2)
    suite = suite()
    tr.run(suite)


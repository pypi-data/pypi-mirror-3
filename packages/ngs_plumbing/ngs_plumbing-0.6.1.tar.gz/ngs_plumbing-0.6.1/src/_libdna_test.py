# This file is part of ngs_plumbing.

# ngs_plumbing is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ngs_plumbing is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with ngs_plumbing.  If not, see <http://www.gnu.org/licenses/>.

# Copyright 2012 Laurent Gautier

import unittest
import io
import struct
import ngs_plumbing._libdna as _libdna

class BitPackingTestCase(unittest.TestCase):

    def test_dna_to_bit2_bytes(self):
        string = b'ATACGCGGCT'+b'GATCGTAGCG'
        vector = _libdna.bit2_frombytes(string)
        string_back = _libdna.byte_frombit2bytes(vector)
        self.assertEqual(string, string_back)

    def test_dna_to_bit2_bytes_lowercase(self):
        string = b'atACGCGGct'+b'gaTCGTAGCG'
        vector = _libdna.bit2_frombytes(string)
        string_back = _libdna.byte_frombit2bytes(vector)
        self.assertEqual(string.upper(), string_back)

    def test_dna_to_bit2_bytearray(self):
        string = b'ATACGCGGCT'+b'GATCGTAGCG'
        vector = _libdna.bit2_frombytearray(bytearray(string))
        string_back = _libdna.byte_frombit2bytearray(vector)
        self.assertEqual(string, string_back)

    # def test_dna_to_bit2_buffer(self):
    #     string = b'ATACGCGGCT'+b'GATCGTAGCG'
    #     vector = _libdna.bit2_frombuffer(string)
    #     string_back = _libdna.byte_frombit2buffer(vector)
    #     self.assertEqual(string, string_back)

    def test_slice_frombit2bytes(self):
        string = b'ATACGCGGCT'+b'GATCGTAGCG'
        packed = _libdna.bit2_frombytes(string)
        chunk = _libdna.slice_frombit2bytes(packed, 0, 4)
        self.assertEqual(string[0:4], chunk)
        chunk = _libdna.slice_frombit2bytes(packed, 0, 8)
        self.assertEqual(string[0:8], chunk)
        chunk = _libdna.slice_frombit2bytes(packed, 3, 6)
        self.assertEqual(string[3:6], chunk)
        chunk = _libdna.slice_frombit2bytes(packed, 2, 4)
        self.assertEqual(string[2:4], chunk)
        chunk = _libdna.slice_frombit2bytes(packed, 0, 11)
        self.assertEqual(string[0:11], chunk)
        chunk = _libdna.slice_frombit2bytes(packed, 3, 11)
        self.assertEqual(string[3:11], chunk)
        chunk = _libdna.slice_frombit2bytes(packed, 4, 11)
        self.assertEqual(string[4:11], chunk)
        chunk = _libdna.slice_frombit2bytes(packed, 3, 12)
        self.assertEqual(string[3:12], chunk)

        #self.assertRaises(IndexError, _libdna.slice_frombit2bytes,
        #                 packed, -1, 3)
        self.assertRaises(IndexError, _libdna.slice_frombit2bytes,
                         packed, 1, 300)
        self.assertRaises(IndexError, _libdna.slice_frombit2bytes,
                         packed, 4, 3)

    def test_slice_frombit2bytearray(self):
        string = bytearray(b'ATACGCGGCT'+b'GATCGTAGCG')
        packed = _libdna.bit2_frombytearray(string)
        chunk = _libdna.slice_frombit2bytearray(packed, 0, 4)
        self.assertEqual(string[0:4], chunk)
        chunk = _libdna.slice_frombit2bytearray(packed, 0, 8)
        self.assertEqual(string[0:8], chunk)
        chunk = _libdna.slice_frombit2bytearray(packed, 3, 6)
        self.assertEqual(string[3:6], chunk)
        chunk = _libdna.slice_frombit2bytearray(packed, 2, 4)
        self.assertEqual(string[2:4], chunk)
        chunk = _libdna.slice_frombit2bytearray(packed, 0, 11)
        self.assertEqual(string[0:11], chunk)
        chunk = _libdna.slice_frombit2bytearray(packed, 3, 11)
        self.assertEqual(string[3:11], chunk)
        chunk = _libdna.slice_frombit2bytearray(packed, 4, 11)
        self.assertEqual(string[4:11], chunk)
        chunk = _libdna.slice_frombit2bytearray(packed, 3, 12)
        self.assertEqual(string[3:12], chunk)

        #self.assertRaises(IndexError, _libdna.slice_frombit2bytes,
        #                 packed, -1, 3)
        self.assertRaises(IndexError, _libdna.slice_frombit2bytearray,
                         packed, 1, 300)
        self.assertRaises(IndexError, _libdna.slice_frombit2bytearray,
                         packed, 4, 3)


        
def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(BitPackingTestCase)
    return suite


def main():
    r = unittest.TestResult()
    suite().run(r)
    return r

if __name__ == "__main__":
    tr = unittest.TextTestRunner(verbosity = 2)
    suite = suite()
    tr.run(suite)


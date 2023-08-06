import unittest
import os
from pyrametros import Row, parse_file

class TestTableParsing(unittest.TestCase):

    def setUp(self):
        abspath = os.path.realpath(__file__)
        self.rows = parse_file(os.path.dirname(abspath)+ "/normal_table.txt")
        self.keys = ['ha', 'hb', 'hc']

    def test_row_keys(self):
        for i in self.rows:
            self.assertEquals( sorted(i.keys()), sorted(self.keys))

    def test_row_values(self):
        self.assertEquals( sorted(self.rows[0].values()), sorted(["a1", "a2", "a3"]))
        self.assertEquals( sorted(self.rows[1].values()), sorted(["b1", "b2", "b3"]))

if __name__ == "__main__":
    unittest.main()

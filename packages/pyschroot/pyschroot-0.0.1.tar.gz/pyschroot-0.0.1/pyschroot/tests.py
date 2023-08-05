# -*- coding: utf-8 -*-

import unittest
from command import Schroot


class TestFunctions(unittest.TestCase):

    def test_simple_command(self):
        c = Schroot('wheezy')
        c.run_cmd('ls', '-lah')
        c.close()


if __name__ == '__main__':
    unittest.main()
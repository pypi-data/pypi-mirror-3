"""
Contains the unittests for genomes
"""

# Internal modules #
from genomes import Assembly

# Unittesting module #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Nosetest flag #
__test__ = True

###################################################################################
class Test(unittest.TestCase):
    def runTest(self):
        a = Assembly('sacCer2')
        tests = [(1,'chrI'),('chr1','chrI'),('chrI','chrI'),('I','chrI')]
        for got,expected in tests:
            got = a.guess_chromosome_name(1)
            self.assertEqual(got, expected)

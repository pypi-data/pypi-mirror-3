import unittest

import rfc3161

class Rfc3161(unittest.TestCase):
    PUBLIC_TSA_SERVER = 'http://time.certum.pl'

    def test_timestamp(self):
        value, substrate = rfc3161.timestamp(self.PUBLIC_TSA_SERVER, data='xx')
        self.assertNotEqual(value, None)
        self.assertEqual(substrate, '')
        print value

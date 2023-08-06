
import os
import tempfile
import unittest

def test_file(name):
    return os.path.join(os.path.dirname(__file__), 'data', name)

class Tmp(object):
    def __init__(self):
        self.path = None

    def __enter__(self):
        assert self.path is None
        (_fd, self.path) = tempfile.mkstemp()
        return self.path

    def __exit__(self, et, e, tb):
        os.unlink(self.path)

class NummTestCase(unittest.TestCase):
    def assertArrayEqual(self, a, b):
        # Note: doesn't compare dtypes.
        msg = 'Expected:\n%r\nGot:\n%r\n' % (a, b)
        self.assertEquals(a.shape, b.shape, msg)
        self.assertTrue((a == b).all(), msg)


import os
import tempfile

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


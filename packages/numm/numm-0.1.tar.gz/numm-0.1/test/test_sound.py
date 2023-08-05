
# XXX: Add a test for audio seeking.

def test_sound2np():
    r"""
    >>> import numm
    >>> import numpy

    >>> import util

    >>> a = numm.sound2np(util.test_file('test.wav'))
    >>> a.shape
    (128, 2)
    >>> ref = numpy.arange(128, dtype=numpy.int16).repeat(2).reshape((128, 2))
    >>> (a == ref).all()
    True
    """

def test_sound2np_n_frames():
    r"""
    >>> import numm
    >>> import numpy

    >>> import util

    >>> a = numm.sound2np(util.test_file('test.wav'), n_frames=64)
    >>> a.shape
    (64, 2)
    >>> a[0:5,:]
    array([[0, 0],
           [1, 1],
           [2, 2],
           [3, 3],
           [4, 4]], dtype=int16)
    """

def test_np2sound():
    r"""
    >>> import numm
    >>> import numpy

    >>> import util

    >>> a = numpy.arange(128, dtype=numpy.int16).repeat(2).reshape((128, 2))

    >>> with util.Tmp() as path:
    ...     numm.np2sound(a, path)
    ...     b = numm.sound2np(path)

    >>> (a == b).all()
    True
    """

def test_sound2np_seek_past_eof():
    r"""
    >>> import numm
    >>> import numpy

    >>> import util

    >>> a = numm.sound2np(util.test_file('test.wav'), start=8192)
    >>> a.shape
    (0, 2)
    """

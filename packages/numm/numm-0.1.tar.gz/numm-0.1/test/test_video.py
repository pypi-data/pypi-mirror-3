
def test_video2np_no_file():
    r"""
    >>> import numm

    >>> numm.video.video2np('no-such-file') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    RuntimeError: ...
    """

def test_video2np():
    r"""
    >>> import numm

    >>> import util

    >>> a = numm.video.video2np(util.test_file('2x2x2.mkv'), n_frames=10)
    >>> a.shape
    (3, 96, 96, 3)
    """

def test_video2np_n_frames():
    r"""
    >>> import numm

    >>> import util

    >>> a = numm.video.video2np(util.test_file('2x2x2.mkv'), n_frames=2)
    >>> a.shape
    (2, 96, 96, 3)
    """

def test_video2np_no_resize():
    r"""
    >>> import numm

    >>> import util

    >>> a = numm.video.video2np(util.test_file('2x2x2.mkv'), height=None)
    >>> a.shape
    (3, 100, 100, 3)
    """

def test_video2np_seek():
    r"""
    >>> import numm

    >>> import util

    >>> a = numm.video.video2np(util.test_file('2x2x2.mkv'), start=1)
    >>> a.shape
    (2, 96, 96, 3)

    XXX: Need to check timestamps here.
    """

def test_np2video():
    r"""
    >>> import numm
    >>> import numpy

    >>> import util

    >>> frames = numpy.zeros((4, 100, 100, 3), numpy.uint8)

    >>> with util.Tmp() as path:
    ...     numm.np2video(frames, path)
    ...     frames2 = numm.video2np(path, height=None)

    >>> frames2.shape
    (4, 100, 100, 3)
    """

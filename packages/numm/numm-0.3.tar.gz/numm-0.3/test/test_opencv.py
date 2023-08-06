
def test_np2cv():
    r"""
    >>> import numm
    >>> import numpy

    >>> a = numpy.arange(6, dtype=numpy.uint8).reshape(2, 3)
    >>> img = numm.opencv.np2cv(a)
    >>> (img.width, img.height, img.depth, img.nChannels)
    (3, 2, 8L, 1)

    >>> a = numpy.arange(18, dtype=numpy.uint8).reshape(2, 3, 3)
    >>> img = numm.opencv.np2cv(a)
    >>> (img.width, img.height, img.depth, img.nChannels)
    (3, 2, 8L, 3)
    """

def test_cv2np():
    r"""
    >>> import cv
    >>> import numm

    >>> img = cv.CreateImage((3, 2), cv.IPL_DEPTH_8U, 1)
    >>> cv.Set(img, 1)
    >>> numm.opencv.cv2np(img)
    array([[[1],
            [1],
            [1]],
    <BLANKLINE>
           [[1],
            [1],
            [1]]], dtype=uint8)

    >>> img = cv.CreateImage((3, 2), cv.IPL_DEPTH_8U, 3)
    >>> cv.Set(img, (1, 2, 3))
    >>> numm.opencv.cv2np(img)
    array([[[1, 2, 3],
            [1, 2, 3],
            [1, 2, 3]],
    <BLANKLINE>
           [[1, 2, 3],
            [1, 2, 3],
            [1, 2, 3]]], dtype=uint8)
    """

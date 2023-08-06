
def test_image():
    r"""
    >>> import numm

    >>> import util

    An image with a white, a blue, a green and a black pixel.

    >>> a = numm.image2np(util.test_file('2x2.png'))
    >>> a.shape
    (2, 2, 3)
    >>> a
    array([[[255, 255, 255],
            [  0,   0, 255]],
    <BLANKLINE>
           [[  0, 255,   0],
            [  0,   0,   0]]], dtype=uint8)
    """

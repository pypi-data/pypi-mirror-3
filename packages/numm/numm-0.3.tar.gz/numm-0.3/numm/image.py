
"""
Conversion between image files and numpy arrays.

Images are represented as arrays with shape (height, width, 3).
"""

import numpy
import Image

def image2np(path):
    "Load an image file into an array."

    im = Image.open(path)
    im = im.convert('RGB')
    np = numpy.asarray(im, dtype=numpy.uint8)
    return np

def np2image(np, path):
    "Save an image array to a file."

    assert np.dtype == numpy.uint8, "nparr must be uint8"
    im = Image.fromstring(
        'RGB', (np.shape[1], np.shape[0]), np.tostring())
    im.save(path)

if __name__ == '__main__':
    # XXX: Replace this with an automated test.
    import sys
    np1 = image2np(sys.argv[1])
    np2image(np1, sys.argv[2])
    np2 = image2np(sys.argv[2])
    print 'error: ', numpy.sum(abs(np1-np2))

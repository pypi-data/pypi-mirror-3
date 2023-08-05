
import cv
import numpy

def np2cv(a, skip_data=False):
    depth = {
        'uint8': cv.IPL_DEPTH_8U,
        'int16': cv.IPL_DEPTH_16S,
        'float32': cv.IPL_DEPTH_32F,
        'float64': cv.IPL_DEPTH_64F,
        }[str(a.dtype)]

    if len(a.shape) == 3:
        n_channels = a.shape[2]
    elif len(a.shape) == 2:
        n_channels = 1
    else:
        raise ValueError(a)

    img = cv.CreateImageHeader((a.shape[1], a.shape[0]), depth, n_channels)
    cv.SetData(img, a.tostring(), a.dtype.itemsize * n_channels * a.shape[1])
    return img

def cv2np(img):
    dtype = {
        cv.IPL_DEPTH_8U: numpy.uint8,
        cv.IPL_DEPTH_16S: numpy.int16,
        cv.IPL_DEPTH_32F: numpy.float32,
        cv.IPL_DEPTH_64F: numpy.float64,
        }[img.depth]
    a = numpy.fromstring(
        img.tostring(),
        dtype=dtype)
    a.shape = (img.height, img.width, img.nChannels)
    return a


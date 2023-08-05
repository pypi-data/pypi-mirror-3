
import numm
import numpy

def gauss_2d(size):
    (x, y) = numpy.mgrid[-size:size + 1, -size:size + 1]
    g = numpy.exp(-(x ** 2 / float(size) + y ** 2 / float(size)))
    g /= g.sum()
    return g

px = 0
py = 0
mode = 1
size = 30
kernel = gauss_2d(size).repeat(3)
kernel = kernel.reshape(size * 2 + 1, size * 2 + 1, 3)
acc = numpy.zeros((240 + size * 2, 320 + size * 2, 3), numpy.uint8)

def mouse_in(type, x, y, b):
    global acc
    global px
    global py
    global i
    global mode

    if type == 'mouse-button-press':
        mode = -1 * mode
    else:
        x = int(x * 320)
        y = int(y * 240)
        size = kernel.shape[0] / 2
        a = acc[y : y + size * 2 + 1, x : x + size * 2 + 1]
        k = kernel * (50 / kernel.max())

        if mode > 0:
            a += k.clip(0, 255 - a)
        else:
            a -= k.clip(0, a)

def video_out(a):
    a[:] = acc[size:-size,size:-size,:]

if __name__ == '__main__':
    numm.run(**globals())

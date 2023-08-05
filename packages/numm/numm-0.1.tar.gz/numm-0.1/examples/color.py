
import numm
import numpy

px = 0
py = 0
i = 0
di = 0

def mouse_in(type, x, y, b):
    global px
    global py
    global di
    px = x
    py = y
    di += 0.05

def video_out(a):
    global i
    global di
    a[:,:,0] = 255 * i * numpy.clip(px, 0, 1)
    a[:,:,2] = 255 * i * numpy.clip((1 - py - px), 0, 1)
    a[:,:,1] = 255 * i * numpy.clip(py, 0, 1)
    i = numpy.clip(i + di, 0, 1)
    di = numpy.clip(di - 0.01, -0.003, 1)

if __name__ == '__main__':
    numm.run(**globals())

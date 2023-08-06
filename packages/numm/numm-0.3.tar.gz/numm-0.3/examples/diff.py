
"Output differences of successive input frames."

import numpy

import numm

s1 = numpy.zeros((240, 320, 3), dtype=numpy.uint8)
s2 = numpy.zeros((240, 320, 3), dtype=numpy.uint8)

def video_in(a):
    global s1
    global s2
    s2 = s1
    s1 = a

def video_out(a):
    f1 = s1
    f2 = s2
    idx1 = f1 > f2
    idx2 = f2 >= f1
    a[idx1] = (f1 - f2)[idx1]
    a[idx2] = (f2 - f1)[idx2]

if __name__ == '__main__':
    numm.run(**globals())

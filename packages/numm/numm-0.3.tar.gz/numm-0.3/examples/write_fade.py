import numm, numpy

dur= 30*10
np = numpy.ones((dur, 240, 320, 3), dtype=numpy.uint8)

for i in range(dur):
    np[i] *= (i/float(dur))*255

numm.np2video(np, 'fade.ogg')

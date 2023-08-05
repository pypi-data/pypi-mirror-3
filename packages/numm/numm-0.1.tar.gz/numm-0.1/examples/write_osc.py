import numm, numpy

dur= 30*5
np = numpy.ones((dur, 240, 320, 3), dtype=numpy.uint8)

for i in range(dur):
    np[i] *= (i/float(dur))*255
    np[i,:,:,i%3] = 255

numm.np2video(np, 'osc.mkv')

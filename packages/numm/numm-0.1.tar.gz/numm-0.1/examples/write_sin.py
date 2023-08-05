import numm, numpy

np = numpy.zeros((44100*10, 2), dtype=numpy.int16)

np[:,0] = pow(2,15)*numpy.sin(
    numpy.linspace(0,10*440*2*numpy.pi, 44100*10))
np[:,1] = np[:,0]

numm.np2sound(np, 'sin.wav')


import numm
import numpy

def audio_out(a):
    a[:,:] = 2**15 * numpy.random.random(a.shape)

def video_out(a):
    a[:,:,:] = 255 * numpy.random.random(a.shape)

if __name__ == '__main__':
    numm.run(**globals())

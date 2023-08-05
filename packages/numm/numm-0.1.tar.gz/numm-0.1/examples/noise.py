
import numm
import numpy

def video_output(a):
    a[:,:,:] = 255 * numpy.random.random(a.shape)

if __name__ == '__main__':
    numm.run(**globals())


import numpy
import numm

# Try this fullscreen in a dark room without headphones.

max_recorded_input = 0
volume_coeff = 1.0
max_brightness = 0
brightness_coeff = 1.0
phase = 0

def audio_input(a):
    global max_recorded_input
    global volume_coeff
    level = numpy.abs(a).mean()
    max_recorded_input = max(max_recorded_input, level)
    volume_coeff = 1 - pow(level / max_recorded_input, 0.5)

def audio_output(a):
    global phase
    t = numpy.arange(phase, a.shape[0] + phase) / 44100.0
    a[:,0] = (2 ** 15 - 1) * numpy.sin(2 * numpy.pi * 440 * t)
    a *= volume_coeff
    a[:,1] = a[:,0]
    phase += a.shape[0]

def video_input(a):
    global max_brightness
    global brightness_coeff

    level = a.mean()
    max_brightness = max(max_brightness, level)
    brightness_coeff = 1 - pow(level / max_brightness, 0.5)

    #last_frame[:] = a

def video_output(a):
    a[:] = 255 * brightness_coeff

if __name__ == '__main__':
    numm.run(**globals())

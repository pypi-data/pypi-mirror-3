
import numm

threshold = 0.5
last = None

def video_in(a):
    global last
    last = a

def video_out(a):
    if last is None:
        return

    a[:] = 0
    a[last > threshold * 128] = 255

def mouse_in(type, px, py, button):
    global threshold

    if type == 'mouse-move':
        print 'threshold = %r' % px
        threshold = px

if __name__ == '__main__':
    numm.run(**globals())

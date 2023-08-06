
import numm

last = None

def video_in(a):
    global last
    last = a

def video_out(a):
    if last is not None:
        a[:] = last

if __name__ == '__main__':
    numm.run(**globals())


import sys

import numm

pos = 0

def mouse_in(t, x, y, b):
    global pos
    pos = x

def video_out(a):
    a[:] = video[pos * video.shape[0]]

if __name__ == '__main__':
    path = sys.argv[1]
    video = numm.video2np(path, n_frames=300, width=320, height=240)
    numm.run(
        mouse_in=mouse_in,
        video_out=video_out)

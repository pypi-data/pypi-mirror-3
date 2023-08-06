
import copy
import termios

LFLAG = 3
CC = 6

def read_mode(fd):
    return termios.tcgetattr(fd)

def write_mode(fd, mode):
    termios.tcsetattr(fd, termios.TCSAFLUSH, mode)

def set_cbreak(mode):
    mode[LFLAG] &= ~(termios.ECHO | termios.ICANON)
    mode[CC][termios.VMIN] = 1
    mode[CC][termios.VTIME] = 0

class Terminal(object):
    def __init__(self, fd):
        self.fd = fd
        self.mode = read_mode(fd)
        self.restore = []

    def __enter__(self):
        self.restore.append(copy.deepcopy(self.mode))

    def __exit__(self, exc_type, exc, tb):
        write_mode(self.fd, self.restore.pop())

    def set_cbreak(self):
        set_cbreak(self.mode)
        write_mode(self.fd, self.mode)

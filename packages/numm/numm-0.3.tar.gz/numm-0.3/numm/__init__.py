
"""
Numerical arts library.
"""

__all__ = (
    'sound2np',
    'np2sound',
    'image2np',
    'np2image',
    'video2np',
    'np2video',
    'Run',
    'run')

try:
    import numm.opencv as opencv
except ImportError:
    opencv = None

from numm.sound import sound2np, np2sound, sound_chunks
from numm.image import image2np, np2image
from numm.video import video2np, np2video, video_frames
from numm.async import Run, run

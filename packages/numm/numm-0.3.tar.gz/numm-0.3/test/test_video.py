
import unittest

import numm
import numpy

import util
import gst

test_video = util.test_file('3x16x16.mkv')

class NummVideoTest(unittest.TestCase):
    def test_video2np_no_file(self):
        self.assertRaises(
            RuntimeError,
            lambda: numm.video2np('no-such-file'))

    def test_video2np(self):
        a = numm.video2np(test_video, n_frames=10)
        self.assertEqual((3, 96, 96, 3), a.shape)

    def test_video2np_n_frames(self):
        a = numm.video2np(test_video, n_frames=2)
        self.assertEqual((2, 96, 96, 3), a.shape)

    def test_video2np_no_resize(self):
        a = numm.video2np(test_video, height=None)
        self.assertEqual((3, 16, 16, 3), a.shape)

    def test_video2np_seek(self):
        a = numm.video2np(test_video, start=1)
        self.assertEqual((2, 96, 96, 3), a.shape)
        # XXX: Need to check timestamps here.

    def test_np2video(self):
        frames = numpy.zeros((4, 100, 100, 3), numpy.uint8)

        with util.Tmp() as path:
            numm.np2video(frames, path)
            frames2 = numm.video2np(path, height=None)

        self.assertEqual((4, 100, 100, 3), frames2.shape)

    def test_video_frames(self):
        frames = list(numm.video_frames(test_video, fps=30))
        self.assertEqual((3, 96, 96, 3), numpy.array(frames).shape)
        self.assertEqual(frames[0].timestamp, 0)
        self.assertEqual(frames[1].timestamp, (gst.SECOND / 30))

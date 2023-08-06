
# XXX: Add a test for audio seeking.

import numm
import numpy

import util

test_sound = util.test_file('test.wav')

class NummSoundTest(util.NummTestCase):
    def test_sound2np(self):
        a = numm.sound2np(test_sound)
        ref = numpy.arange(128).repeat(2).reshape((128, 2))
        self.assertEqual(numpy.int16, a.dtype)
        self.assertArrayEqual(ref, a)

    def test_sound2np_n_frames(self):
        a = numm.sound2np(test_sound, n_frames=64)
        ref = numpy.arange(64).repeat(2).reshape((64, 2))
        self.assertEqual(numpy.int16, a.dtype)
        self.assertArrayEqual(ref, a)

    def test_np2sound(self):
        a = numpy.arange(128, dtype=numpy.int16).repeat(2).reshape((128, 2))

        with util.Tmp() as path:
            numm.np2sound(a, path)
            b = numm.sound2np(path)

        self.assertEqual(a.dtype, b.dtype)
        self.assertArrayEqual(a, b)

    def test_sound2np_seek_past_eof(self):
        a = numm.sound2np(test_sound, start=8192)
        self.assertEqual((0, 2), a.shape)

    def test_sound_chunks(self):
        frames = list(numm.sound_chunks(test_sound))
        self.assertEqual((128, 2), numpy.concatenate(frames).shape)
        self.assertEqual(frames[0].timestamp, 0)

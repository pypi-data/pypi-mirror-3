
import unittest

import gobject
import gst

import numm
import numpy

class NummAsyncTest(unittest.TestCase):
    def setUp(self):
        self.loop = gobject.MainLoop()

    def stop(self):
        self.loop.quit()

    def run_run(self, run, timeout=3000):
        def play():
            run.pipeline.set_state(gst.STATE_PLAYING)
            return False

        def oops():
            self.stop()
            return False

        gobject.idle_add(play)
        gobject.timeout_add(timeout, oops)
        self.loop.run()
        self.assertEquals(
            gst.STATE_CHANGE_SUCCESS,
            run.pipeline.set_state(gst.STATE_NULL))

class AsyncVideoInTest(NummAsyncTest):
    def test(self):
        arrays = []

        def video_in(a):
            arrays.append(a)
            self.stop()

        src = gst.element_factory_make('videotestsrc')
        run = numm.Run(video_in=video_in, video_src=src)
        self.run_run(run)
        self.assertEquals(1, len(arrays))
        self.assertEquals((240, 320, 3), arrays[0].shape)
        self.assertEquals(0, arrays[0].timestamp)

class AsyncVideoOutTest(NummAsyncTest):
    def test(self):
        arrays = []

        def buffer(pad, buf):
            a = numpy.fromstring(buf, numpy.uint8)
            arrays.append(a)
            self.stop()

        def video_out(a):
            self.assertTrue((a == 0).all())
            self.assertEquals(0, a.timestamp)
            a[:] = 42

        sink = gst.element_factory_make('fakesink')
        run = numm.Run(video_out=video_out, video_sink=sink)
        src = run.pipeline.get_by_name('video_out')
        pad = src.get_pad('src')
        pad.add_buffer_probe(buffer)
        self.run_run(run)
        self.assertEquals(1, len(arrays))
        self.assertEquals((240 * 320 * 3,), arrays[0].shape)
        self.assertTrue((arrays[0] == 42).all())

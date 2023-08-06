# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
# GPL 2008-2010

from __future__ import division

import Queue

import pygst
pygst.require('0.10')

import gst
import gobject
import numpy

import numm.io
from numm.async import NummBuffer

def _multiple_of_four(n):
    return 4*int(n/4)

def _width_for_height(caps, height):
    assert 'width' in caps[0].keys()
    assert 'height' in caps[0].keys()
    c_width = caps[0]['width']
    c_height = caps[0]['height']
    assert isinstance(c_width, int)
    assert isinstance(c_height, int)
    return _multiple_of_four(c_width / c_height * height)

def _height_for_width(caps, width):
    assert 'width' in caps[0].keys()
    assert 'height' in caps[0].keys()
    c_width = caps[0]['width']
    c_height = caps[0]['height']
    assert isinstance(c_width, int)
    assert isinstance(c_height, int)
    return _multiple_of_four(c_height / c_width * width)

def _calculate_size(caps, height):
    if 'width' in caps[0].keys() and isinstance(caps[0]['width'], int):
        width = int(caps[0]['width']/caps[0]['height'] * height)
    else:
        width = int(4/3 * height)

        if width % 4:
            width += 4 - width % 4

        if height % 4:
            height += 4 - height % 4

    return (width, height)

def _make_video_pipeline(path, width, height, framerate):
    pipeline = gst.parse_launch('''
        filesrc name=filesrc !
        decodebin2 name=decodebin !
        videorate !
        videoscale !
        ffmpegcolorspace name=colorspace

        appsink name=sink sync=false
        ''')

    src = pipeline.get_by_name('filesrc')
    src.props.location = path

    sbin = pipeline.get_by_name('decodebin')
    sbin.props.caps = gst.Caps("video/x-raw-yuv;video/x-raw-rgb")
    sbin.props.expose_all_streams = False

    def pad_caps_changed(pad, pspec):
        pad_caps = pad.get_caps()

        if not (pad_caps[0].has_field('width') and isinstance(pad_caps[0]['width'], int)):
            return

        csp = pipeline.get_by_name('colorspace')
        csp_pad = csp.get_pad('src')

        if csp_pad.get_peer() is not None:
            # This pad is already linked!
            return

        caps = gst.Caps(
           "video/x-raw-rgb, "
           "bpp = (int) 24, depth = (int) 24, "
           "endianness = (int) BIG_ENDIAN, "
           "red_mask = (int) 0x00FF0000, "
           "green_mask = (int) 0x0000FF00, "
           "blue_mask = (int) 0x000000FF, "
           "pixel-aspect-ratio = (fraction) 1/1")
        caps[0]['framerate'] = framerate

        # In principle, the width and height of the input video are
        # known (fixed) at this time, so we can calculate the missing
        # output dimension from the known output dimension and the
        # input dimensions.

        if width is not None and height is not None:
            caps[0]['width'] = _multiple_of_four(width)
            caps[0]['height'] = _multiple_of_four(height)
        elif width is None and height is not None:
            h = _multiple_of_four(height)
            caps[0]['height'] = h
            caps[0]['width'] = _width_for_height(pad_caps, h)
        elif height is None and width is not None:
            w = _multiple_of_four(width)
            caps[0]['width'] = w
            caps[0]['height']  = _height_for_width(pad_caps, w)

        csp.link(sink, caps)

    def src_bin_pad_added_cb(_sbin, pad):
        pad_caps = pad.get_caps()

        if not pad_caps[0].get_name().startswith('video/'):
            return

        pad.connect('notify::caps', pad_caps_changed)
        pad_caps_changed(pad, None)

    sbin.connect('pad-added', src_bin_pad_added_cb)
    sink = pipeline.get_by_name('sink')
    return (pipeline, sink)

class VideoReader(numm.io.Reader):
    def __init__(self, path, cb, width=None, height=96, fps=30, start=0,
                 n_frames=-1):
        framerate = gst.Fraction(fps, 1)
        (pipeline, appsink) = _make_video_pipeline(
            path, width, height, framerate)
        numm.io.Reader.__init__(self, pipeline, appsink)

        self.cb = cb
        self.fps = fps
        self.start = start
        self.n_frames = n_frames

        self.next_frame = 0
        self.last_timestamp = -1
        self.seek_done = False
        self.shape = None

    def _do_seek(self):
        # XXX: Check return value?
        self.pipeline.seek_simple(
            gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_ACCURATE,
            int(self.start * gst.SECOND / float(self.fps)))

    def _new_buffer(self, _appsink):
        numm.io.Reader._new_buffer(self, _appsink)
        buffer = self.pull()

        if self.start != 0 and not self.seek_done:
            self.seek_done = True
            #print 'seeking to %d' % (int(start*gst.SECOND/float(fps)))
            gobject.idle_add(self._do_seek)
            return

        if self.n_frames > 0 and self.next_frame >= self.n_frames:
            # We've already gotten as many frames as we want; stop.
            return

        if buffer.timestamp <= self.last_timestamp:
            # This looks like a duplicate buffer. This seems to happen
            # when we seek sometimes.
            return True

        if self.shape is None:
            caps = buffer.caps
            w = caps[0]['width']
            h = caps[0]['height']
            n_bytes = w * h * 3
            assert len(buffer) == n_bytes, (
                "buffer length (%d) != w * h * 3 (%d)" % (
                    len(buffer), n_bytes))
            self.shape = (h, w, 3)

        a = numpy.fromstring(buffer, dtype=numpy.uint8).reshape(self.shape).view(NummBuffer)
        a.timestamp = buffer.timestamp

        self.cb(a)
        self.next_frame += 1
        self.last_timestamp = buffer.timestamp

def _read_video(path, cb, **kw):
    loader = VideoReader(path, cb, **kw)
    r = numm.io.RunPipeline(loader.pipeline)

    for _ in r.run():
        pass

def video_frames(path, **kw):
    q = Queue.Queue(1)

    def cb(frame):
        q.put(frame)

    loader = VideoReader(path, cb, **kw)
    r = numm.io.RunPipeline(loader.pipeline)

    for _ in r.run():
        while q.qsize() > 0:
            yield q.get()

    while q.qsize() > 0:
        yield q.get()

def _write_video(np, filepath, opts={}):
    defaults = {
        'width': np.shape[2],
        'height': np.shape[1],
        'fps': 30}
    options = dict(defaults)
    options.update(opts)

    pipeline = gst.parse_launch(
        '''
        appsrc name=appsrc ! 
        video/x-raw-rgb, bpp=(int)24, depth=(int)24, endianness=(int)BIG_ENDIAN,red_mask=(int)0x00FF0000,green_mask=(int)0x0000FF00,blue_mask=(int)0x000000FF,width=(int)%(width)d, height=(int)%(height)d, framerate=(fraction)%(fps)d/1 !
        ffmpegcolorspace ! 
        videorate !
        jpegenc !
        matroskamux !
        filesink name=filesink
        ''' % options)

    def get_chunk(position, length):
        return (1, np[position])

    appsrc = pipeline.get_by_name('appsrc')
    appsrc.props.blocksize = options['width'] * options['height'] * 3

    filesink = pipeline.get_by_name('filesink')
    filesink.props.location = filepath

    numm.io._run_appsrc_pipeline(pipeline, appsrc, get_chunk)

def video2np(path, width=None, height=96, fps=30, start=0, n_frames=-1):
    "Load video data from a file."

    # XXX: Ideally we could get the number of buffers beforehand to
    # avoid having to store all the buffers before allocating the
    # output array.

    frames = []

    def loaded_frame(frame):
        frames.append(frame)

    _read_video(path, loaded_frame, width=width, height=height, fps=fps, start=start, n_frames=n_frames)

    if frames:
        (height, width) = frames[0].shape[:2]
        a = numpy.ndarray((len(frames), height, width, 3), dtype=numpy.uint8)

        for (i, frame) in enumerate(frames):
            a[i,:,:,:] = frame
    else:
        a = numpy.ndarray((0, height, width, 3))

    return a

def np2video(np, path):
    """
    Save video data to a file.

    Currently, the video data is written as JPEG images in a Matroska
    container.
    """

    # XXX: audio?
    _write_video(np, path)

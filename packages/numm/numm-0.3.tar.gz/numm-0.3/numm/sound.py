
"""
Conversion between audio files and numpy arrays.

Audio data is represented by arrays of shape (n_frames, n_channels),
with a sample rate of 44.1kHz by default.
"""

import Queue

import pygst
pygst.require('0.10')

import gobject

import gst
import numpy

import numm.io
from numm.async import NummBuffer

def _make_sound_pipeline(path, sample_rate):
    pipeline = gst.parse_launch(
        '''
        filesrc name=filesrc !
        decodebin !
        audioconvert !
        audioresample !
        audio/x-raw-int,rate=%s,width=16,depth=16,signed=true !
        appsink name=appsink
        ''' % (sample_rate))

    filesrc = pipeline.get_by_name('filesrc')
    filesrc.props.location = path

    appsink = pipeline.get_by_name('appsink')
    return (pipeline, appsink)

class SoundReader(numm.io.Reader):
    def __init__(self, path, cb, sample_rate=44100, start=0, n_frames=-1):
        # XXX: These caps ought to be kept in sync with the ones in numm.run.
        (pipeline, appsink) = _make_sound_pipeline(path, sample_rate)
        numm.io.Reader.__init__(self, pipeline, appsink)

        self.cb = cb
        self.sample_rate = sample_rate
        self.start = start
        self.n_frames = n_frames

        self.frame_idx = 0
        self.seek_done = False
        self.n_channels = None

    def _do_seek(self):
        # XXX: Check return value?
        self.pipeline.seek_simple(
            gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_ACCURATE,
            int(self.start * gst.SECOND / float(self.sample_rate)))

    def _new_buffer(self, _appsink):
        numm.io.Reader._new_buffer(self, _appsink)
        buffer = self.pull()

        if self.start != 0 and not self.seek_done:
            self.seek_done = True
            #print 'seeking to %d' % (int(start*gst.SECOND/float(sample_rate)))
            gobject.idle_add(self._do_seek)
            return True

        if self.n_channels is None:
            self.n_channels = buffer.caps[0]['channels']

        l = len(buffer) / (2 * self.n_channels)
        np = numpy.fromstring(buffer, numpy.int16).reshape(l, self.n_channels).view(NummBuffer)
        np.timestamp = buffer.timestamp

        if self.n_frames > 0 and self.frame_idx + np.shape[0] >= self.n_frames:
            self.cb(np[:self.n_frames - self.frame_idx])
            return False

        self.frame_idx += np.shape[0]
        self.cb(np)
        return True

    # numm.io._run_appsink_pipeline(pipeline, appsink, loaded_buffer)

def _read_sound(path, cb, **kw):
    loader = SoundReader(path, cb, **kw)
    r = numm.io.RunPipeline(loader.pipeline)

    try:
        r.start()

        while not r.done:
            r.step()
    finally:
        r.stop()

    if r.errors:
        raise r.errors[0]

def sound_chunks(path, **kw):
    def cb(a):
        q.put(a)

    loader = SoundReader(path, cb, **kw)
    r = numm.io.RunPipeline(loader.pipeline)
    q = Queue.Queue(1)

    for _ in r.run():
        while q.qsize() > 0:
            yield q.get()

    while q.qsize() > 0:
        yield q.get()

def _write_sound(np, filepath, sample_rate=44100):
    pipeline = gst.parse_launch(
        '''
        appsrc name=appsrc !
        audio/x-raw-int,rate=%s,width=16,depth=16,channels=2,signed=true !
        wavenc !
        filesink name=filesink
        ''' % (sample_rate))

    def get_chunk(position, length):
        return (length, np[position:position+length])

    appsrc = pipeline.get_by_name('appsrc')

    filesink = pipeline.get_by_name('filesink')
    filesink.props.location = filepath

    numm.io._run_appsrc_pipeline(pipeline, appsrc, get_chunk)

def sound2np(filepath, start=0, n_frames=-1, sample_rate=44100):
    """
    Load audio data from a file.
    """

    arrays = []

    def cb(a):
        arrays.append(a)

    _read_sound(filepath, cb, start=start, n_frames=n_frames, sample_rate=sample_rate)

    if arrays:
        return numpy.concatenate(arrays)
    else:
        return numpy.ndarray((0, 2))

def np2sound(np, filepath):
    """
    Save audio data to a file.

    Currently, audio is always saved as WAV data.
    """

    _write_sound(np, filepath)

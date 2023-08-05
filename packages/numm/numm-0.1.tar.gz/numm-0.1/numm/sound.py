
"""
Conversion between audio files and numpy arrays.

Audio data is represented by arrays of shape (n_frames, n_channels),
with a sample rate of 44.1kHz by default.
"""

import pygst
pygst.require('0.10')

import gobject

import gst
import numpy

import numm.load

def _read_sound(filepath, sample_rate=44100, start=0, n_frames=-1):
    # XXX: These caps ought to be kept in sync with the ones in numm.run.
    pipeline = gst.parse_launch(
        '''
        filesrc name=filesrc !
        decodebin !
        audioconvert !
        audio/x-raw-int,rate=%s,width=16,depth=16,signed=true !
        appsink name=appsink
        ''' % (sample_rate))

    filesrc = pipeline.get_by_name('filesrc')
    filesrc.props.location = filepath

    appsink = pipeline.get_by_name('appsink')
    n_channels = None

    def do_seek():
        # XXX: Check return value?
        pipeline.seek_simple(
            gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_ACCURATE,
            int(start * gst.SECOND / float(sample_rate)))

    frame_idx = 0
    seek_done = False

    for buffer in numm.load._run_appsink_pipeline(pipeline, appsink):
        if start != 0 and not seek_done:
            seek_done = True
            #print 'seeking to %d' % (int(start*gst.SECOND/float(sample_rate)))
            gobject.idle_add(do_seek)
            continue

        if n_channels is None:
            n_channels = buffer.caps[0]['channels']

        l = len(buffer) / (2 * n_channels)
        np = numpy.fromstring(buffer, numpy.int16).reshape(l, n_channels)

        if n_frames > 0 and frame_idx + np.shape[0] >= n_frames:
            yield np[:n_frames-frame_idx]
            break

        frame_idx += np.shape[0]
        yield np

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

    numm.load._run_appsrc_pipeline(pipeline, appsrc, get_chunk)

def sound2np(filepath, start=0, n_frames=-1):
    """
    Load audio data from a file.
    """

    arrays = list(_read_sound(filepath, start=start, n_frames=n_frames))

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

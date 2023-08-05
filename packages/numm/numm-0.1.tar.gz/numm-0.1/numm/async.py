
"""
Asynchronous looping interface.
"""

try:
    import cProfile as profile
except ImportError:
    import profile

import os
import sys
import threading

import gobject
import pygst
pygst.require("0.10")
import gst
import numpy

__all__ = (
    'Run',
    'run')

callbacks = (
    'audio_in',
    'audio_out',
    'video_in',
    'video_out',
    'mouse_in',
    'keyboard_in',
    )

audio_caps = gst.Caps(','.join([
     'audio/x-raw-int',
     'channels=2,'
     'rate=44100',
     'signed=true',
     'depth=16',
     'width=16',
     # XXX: needs to be host endianness?
     'endianness=1234']))

video_caps = gst.Caps(','.join([
    'video/x-raw-rgb',
    'bpp=24',
    'depth=24',
    'endianness=4321',
    'red_mask=16711680',
    'green_mask=65280',
    'blue_mask=255',
    'framerate=30/1',
    'width=320',
    'height=240']))

def _make_video_in_bin(src=None):
    if src is None:
        src = 'autovideosrc'

    bin = gst.parse_bin_from_description('''
        %s !
        ffmpegcolorspace !
        videoscale !
        capsfilter name=videocaps2 !
        appsink name=video_in emit-signals=true
        ''' % (src,), False)

    videofilter = bin.get_by_name('videocaps2')
    videofilter.props.caps = video_caps
    return bin

def _make_video_out_bin(sink=None):
    if sink is None:
        if sys.platform.startswith('win'):
            # Work around the fact that autovideosink attempts
            # d3dvideosink, which sometimes doesn't work.
            sink = "directdrawsink"
        else:
            sink = "autovideosink"

    bin = gst.parse_bin_from_description('''
        appsrc name=video_out block=true is-live=true !
        capsfilter name=videocaps !
        tee name=tee

        tee. !
            queue2 !
            ffmpegcolorspace !
            %s async=false name=video_sink

        tee. !
            queue2 !
            valve name=video_capture_valve drop=true !
            pngenc snapshot=false !
            multifilesink async=false name=video_capture_sink
        ''' % sink, False)

    capsfilter = bin.get_by_name('videocaps')
    capsfilter.props.caps = video_caps
    return bin

def _make_audio_out_bin():
    bin = gst.parse_bin_from_description('''
        appsrc name=audio_out block=true is-live=true !
        capsfilter name=audiocaps !
        audioconvert !
        autoaudiosink
        ''', False)

    audiofilter = bin.get_by_name('audiocaps')
    audiofilter.props.caps = audio_caps
    return bin

def _make_audio_in_bin():
    bin = gst.parse_bin_from_description('''
        autoaudiosrc !
        audioconvert !
        capsfilter name=audiocaps2 !
        appsink name=audio_in emit-signals=true
        ''', False)

    audiofilter = bin.get_by_name('audiocaps2')
    audiofilter.props.caps = audio_caps
    return bin

class Lockable(object):
    "Synchronization utility mixin."

    def __init__(self):
        self.lock = threading.Lock()

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, et, e, tb):
        self.lock.release()

class Run(Lockable):
    """
    Asynchronous looping interface.

    This class converts inputs to numpy arrays and outputs from numpy
    arrays. I/O is done using a set of callbacks.

    When video output is being produced, the following key bindings
    are defined by default:

     - F10 toggles video capture. See L{begin_video_capture}.
     - F11 triggers profiling. See L{profile_all}.
    """

    video_capture_pattern = 'numm-capture-%03d-%%06d.png'

    def __init__(
            self,
            audio_out=None,
            video_out=None,
            audio_in=None,
            video_in=None,
            mouse_in=None,
            keyboard_in=None,
            exit_on_window_close=True,
            video_src=None,
            video_sink=None,
            **kw):
        """
        This class takes a set of callbacks and, when L{run} is
        called, runs in a loop, calling them as appropriate.

        Audio and video callback take an array which contains data which
        was input (in the case of the "_in" functions) or to which data to
        be output should be written (in the case of the "_out" functions).

        If C{video_out} is specified, a window is created for video output.

        The C{keyboard_in} function takes an event type, and a string
        representing the key. The event type is either "key-press" or
        "key-release".

        The C{mouse_in} function takes an event type, X and Y positions,
        and a button. The event type is "mouse-move" or
        "mouse-button-press" or "mouse-button-release".

        @param audio_in: Audio input received.
        @param audio_out: Audio output wanted.
        @param video_in: Video input received.
        @param video_out: Video output wanted.
        @param keyboard_in: Keyboard input received.
        @param mouse_in: Mouse input received.
        @param exit_on_window_close: Whether the L{run} method should
            return when the output window (if any) is closed.
        @type: Boolean.
        @param video_src: The GStreamer element to use as a source for
            video input.
        @type: String.
        @param video_sink: The GStreamer element to use as a source for
            video input.
        @type: String.
        """

        # The lock is currently only used to coordinate print calls.
        Lockable.__init__(self)
        gobject.threads_init()

        self.audio_in = audio_in or kw.get('audio_input')
        self.audio_out = audio_out or kw.get('audio_output')
        self.video_in = video_in or kw.get('video_input')
        self.video_out = video_out or kw.get('video_output')
        self.mouse_in = mouse_in
        self.keyboard_in = keyboard_in
        self.exit_on_window_close = exit_on_window_close
        self.pipeline = gst.Pipeline()
        self.loop = gobject.MainLoop()
        self.capture = 0

        if self.audio_in is not None:
            self.pipeline.add(_make_audio_in_bin())
            appsink = self.pipeline.get_by_name('audio_in')
            appsink.connect('new-buffer', self._got_audio_data)

        if self.audio_out is not None:
            self.pipeline.add(_make_audio_out_bin())
            appsrc = self.pipeline.get_by_name('audio_out')
            appsrc.connect('need-data', self._need_audio_data)

        if self.video_in is not None:
            self.pipeline.add(_make_video_in_bin(video_src))
            appsink = self.pipeline.get_by_name('video_in')
            appsink.connect('new-buffer', self._got_video_data)

        if self.video_out is not None:
            self.pipeline.add(_make_video_out_bin(video_sink))
            appsrc = self.pipeline.get_by_name('video_out')
            appsrc.connect('need-data', self._need_video_data)
            srcpad = appsrc.get_pad('src')
            srcpad.set_event_function(self._video_out_event)

        bus = self.pipeline.get_bus()
        bus.set_sync_handler(self._bus_message)

    def _need_video_data(self, appsrc, n):
        # n represents the amount of data needed in some way
        a = numpy.zeros((240, 320, 3), dtype=numpy.uint8)
        self.video_out(a)
        buf = gst.Buffer(a)
        appsrc.emit('push-buffer', buf)

    def _need_audio_data(self, appsrc, n):
        a = numpy.zeros([n, 2], dtype=numpy.int16)
        self.audio_out(a)
        buf = gst.Buffer(a)
        appsrc.emit('push-buffer', buf)

    def _got_audio_data(self, appsink):
        buffer = appsink.emit('pull-buffer')
        a = numpy.fromstring(buffer, dtype=numpy.int16)
        a = a.reshape((a.shape[0] / 2, 2))
        self.audio_in(a)

    def _got_video_data(self, appsink):
        buffer = appsink.emit('pull-buffer')
        a = numpy.fromstring(buffer, dtype=numpy.uint8)
        a = a.reshape((240, 320, 3))
        self.video_in(a)

    def _bus_message(self, bus, message):
        if message.type == gst.MESSAGE_ERROR:
            (gerror, err_str) = message.parse_error()
            video_sink = self.pipeline.get_by_name('video_sink')

            if (self.exit_on_window_close and
                video_sink is not None and
                message.src in video_sink.elements() and
                gerror.domain == gst.RESOURCE_ERROR and
                gerror.code == gst.RESOURCE_ERROR_NOT_FOUND):
                self.loop.quit()
            else:
                print message

        return gst.BUS_PASS

    def run(self):
        "Enter the mainloop."
        self.pipeline.set_state(gst.STATE_PLAYING)
        self.loop.run()

    def _mouse_event(self, type, pointer_x, pointer_y, button):
        # type is mouse-button-press or mouse-button-release or mouse-move

        if self.mouse_in is not None:
            w = video_caps[0]['width']
            h = video_caps[0]['height']
            self.mouse_in(
                type,
                pointer_x / float(w),
                pointer_y / float(h),
                button)

    def _keyboard_event(self, type, key):
        # type is key-press or key-release

        if self.keyboard_in is not None:
            if not self.keyboard_in(type, key):
                if type == 'key-press':
                    if key == 'F10':
                        self.toggle_video_capture()
                    elif key == 'F11':
                        self.profile_all()

    def _event(self, event):
        type = event['event']

        if type in ('mouse-move', 'mouse-button-press', 'mouse-button-release'):
            self._mouse_event(
                type, event['pointer_x'], event['pointer_y'], event['button'])
        elif type in ('key-press', 'key-release'):
            self._keyboard_event(type, event['key'])
        else:
            print 'unknown event: %r' % event

    def _video_out_event(self, pad, event):
        if event.type == gst.EVENT_NAVIGATION:
            struct = event.get_structure()

            try:
                self._event(dict(struct))
            finally:
                pad.event_default(event)
        else:
            pad.event_default(event)

    def _find_next_capture_index(self):
        # Find a capture filename sequence that doesn't look like it's
        # being used. This is not race-free, but avoids most cases of
        # overwriting capture files.

        while os.path.exists(self.video_capture_pattern % self.capture % 0):
            self.capture += 1

    def begin_video_capture(self):
        """
        Begin capturing video output frames to disk.

        Frames are captured as a series of PNGs.
        """

        sink = self.pipeline.get_by_name('video_capture_sink')
        sink.props.index = 0
        self._find_next_capture_index()
        sink.props.location = self.video_capture_pattern % self.capture
        self.capture += 1
        valve = self.pipeline.get_by_name('video_capture_valve')
        valve.props.drop = False

    def end_video_capture(self):
        "Complement to L{begin_video_capture}."
        valve = self.pipeline.get_by_name('video_capture_valve')
        valve.props.drop = True

    def toggle_video_capture(self):
        valve = self.pipeline.get_by_name('video_capture_valve')
        print valve

        if valve.props.drop:
            print 'begin'
            self.begin_video_capture()
        else:
            print 'end'
            self.end_video_capture()

    def profile_all(self):
        """
        Profile each callback the next time it is called.

        Profiling results are printed to standard output.
        """

        def setup(name):
            orig = getattr(self, name)

            def do_profile(*args):
                p = profile.Profile()
                p.runcall(orig, *args)

                with self:
                    print '%s:' % name
                    p.print_stats(sort='cumulative')

                setattr(self, name, orig)

            if orig is not None:
                setattr(self, name, do_profile)

        setup('audio_in')
        setup('audio_out')
        setup('video_in')
        setup('video_out')

def run(**kw):
    """
    Asynchronous looping interface.

    This function is a shorthand for instantiating L{Run} and calling
    L{run<Run.run>} on the instance; it takes the same arguments as L{Run}.
    """

    # Point of inversion of control.
    run = Run(**kw)
    run.run()



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
import time

import gobject
import pygst
pygst.require("0.10")
import gst
import numpy

import numm.term

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
        src = gst.element_factory_make('autovideosrc')

    bin = gst.parse_bin_from_description('''
        ffmpegcolorspace name=csp !
        videoscale !
        capsfilter name=videocaps2 !
        appsink name=video_in emit-signals=true
        ''', False)

    bin.add(src)
    csp = bin.get_by_name('csp')
    src.link(csp)

    videofilter = bin.get_by_name('videocaps2')
    videofilter.props.caps = video_caps
    return bin

def _make_video_out_bin(sink=None):
    if sink is None:
        if sys.platform.startswith('win'):
            # Work around the fact that autovideosink attempts
            # d3dvideosink, which sometimes doesn't work.
            sink = gst.element_factory_make("directdrawsink")
        else:
            sink = gst.element_factory_make("autovideosink")

    sink.props.name = 'video_sink'

    if hasattr(sink.props, 'async'):
        # Since we have a tee, we need to go synchronously to the
        # PAUSED state to avoid hanging in preroll.
        sink.props.async = False

    bin = gst.parse_bin_from_description('''
        appsrc name=video_out format=time !
        capsfilter name=videocaps !
        tee name=tee

        tee. !
            queue2 !
            ffmpegcolorspace !
            cairotextoverlay name=text halign=right valign=top
                font-desc='Sans 10'

        tee. !
            valve name=video_capture_valve drop=true !
            queue2 !
            pngenc snapshot=false !
            multifilesink async=false name=video_capture_sink
        ''', False)

    bin.add(sink)
    text = bin.get_by_name('text')
    text.link(sink)

    capsfilter = bin.get_by_name('videocaps')
    capsfilter.props.caps = video_caps
    return bin

def _make_audio_out_bin():
    bin = gst.parse_bin_from_description('''
        appsrc name=audio_out block=true is-live=true !
        capsfilter name=audiocaps !
        audioconvert !
        autoaudiosink name=audio_sink
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

class NummBuffer(numpy.ndarray):
    # This subclass exists so that we can set extra attributes
    # (specifically, a timestamp).

    pass

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

     - F9 toggles a frames-per-second display.
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

        self.exit_on_window_close = exit_on_window_close
        self.pipeline = gst.Pipeline()
        self.loop = gobject.MainLoop()
        self.capture = 0
        self.frames_out = 0
        self.frames_out_prev = 0
        self.fps_timeout_id = None
        self.fps_timestamp = None
        self.video_src_spec = video_src
        self.video_sink_spec = video_sink

        self.set_video_out(video_out or kw.get('video_output'))
        self.set_audio_in(audio_in or kw.get('audio_input'))
        self.set_audio_out(audio_out or kw.get('audio_output'))
        self.set_video_in(video_in or kw.get('video_input'))
        self.set_keyboard_in(keyboard_in)
        self.set_mouse_in(mouse_in)

        bus = self.pipeline.get_bus()
        bus.set_sync_handler(self._bus_message)

    def _get_stream_position(self):
        try:
            (pos, _fmt) = self.pipeline.query_position(gst.FORMAT_TIME)
        except gst.QueryError:
            pos = 0

        return pos

    def _sync_state(self, element):
        (status, state, pending) = self.pipeline.get_state()

        if status != gst.STATE_CHANGE_SUCCESS:
            raise RuntimeError

        if pending != gst.STATE_VOID_PENDING:
            element.set_state(pending)
        else:
            element.set_state(state)

    def _got_audio_data(self, appsink):
        buffer = appsink.emit('pull-buffer')
        a = numpy.fromstring(buffer, dtype=numpy.int16).view(NummBuffer)
        a = a.reshape((a.shape[0] / 2, 2))
        a.timestamp = buffer.timestamp

        # XXX
        if self.audio_in:
            self.audio_in(a)

    def set_audio_in(self, callback):
        self.audio_in = callback

        bin = self.pipeline.get_by_name('audio_in_bin')

        if bin is not None or callback is None:
            # XXX: Remove bin if callback is None.
            return

        bin = _make_audio_in_bin()
        bin.props.name = 'audio_in_bin'
        self.pipeline.add(bin)
        appsink = bin.get_by_name('audio_in')
        appsink.connect('new-buffer', self._got_audio_data)
        self._sync_state(bin)

    def _need_audio_data(self, appsrc, n):
        sink = self._get_actual_audio_sink()
        latency = sink.get_latency()
        pos = self._get_stream_position()
        a = numpy.zeros([n, 2], dtype=numpy.int16).view(NummBuffer)
        a.timestamp = pos + latency

        # XXX
        if self.audio_out:
            self.audio_out(a)

        buf = gst.Buffer(a)
        appsrc.emit('push-buffer', buf)

    def set_audio_out(self, callback):
        self.audio_out = callback
        bin = self.pipeline.get_by_name('audio_out_bin')

        if bin is not None or callback is None:
            # XXX: Remove bin if callback is None.
            return

        bin = _make_audio_out_bin()
        bin.props.name = 'audio_out_bin'
        self.pipeline.add(bin)
        appsrc = bin.get_by_name('audio_out')
        appsrc.connect('need-data', self._need_audio_data)
        self._sync_state(bin)

    def _got_video_data(self, appsink):
        buffer = appsink.emit('pull-buffer')
        a = numpy.fromstring(buffer, dtype=numpy.uint8).view(NummBuffer)
        a = a.reshape((240, 320, 3))
        a.timestamp = buffer.timestamp

        # XXX
        if self.video_in:
            self.video_in(a)

    def set_video_in(self, callback):
        self.video_in = callback
        bin = self.pipeline.get_by_name('video_in_bin')

        if bin is not None or callback is None:
            # XXX: Remove bin if callback is None.
            return

        bin = _make_video_in_bin(self.video_src_spec)
        bin.props.name = 'video_in_bin'
        self.pipeline.add(bin)
        appsink = bin.get_by_name('video_in')
        appsink.connect('new-buffer', self._got_video_data)
        self._sync_state(bin)

    def _need_video_data(self, appsrc, n):
        sink = self._get_actual_video_sink()

        if self.frames_out == 0:
            # This seems like as good a place as any to make the video
            # sink not block on the clock.

            try:
                sink.props.sync = False
            except AttributeError:
                pass

        pos = self._get_stream_position()
        latency = sink.get_latency()
        a = numpy.zeros((240, 320, 3), dtype=numpy.uint8).view(NummBuffer)
        a.timestamp = pos + latency

        # XXX
        if self.video_out:
            self.video_out(a)

        buf = gst.Buffer(a)
        buf.offset = self.frames_out

        framerate = float(video_caps[0]['framerate'])
        # I don't know why this works, but it does. Not adding the
        # offset into the future seems to result in the stream time
        # (the one obtained by the query_position() call above)
        # failing to progress after a while.

        # here be dragons!
        buf.timestamp = pos # + int(gst.SECOND / framerate)
        appsrc.emit('push-buffer', buf)
        self.frames_out += 1
        return True

    def set_video_out(self, callback):
        self.video_out = callback
        bin = self.pipeline.get_by_name('video_out_bin')

        if bin is not None or callback is None:
            # XXX: Remove bin if callback is None.
            return

        bin = _make_video_out_bin(self.video_sink_spec)
        bin.props.name = 'video_out_bin'
        self.pipeline.add(bin)
        appsrc = bin.get_by_name('video_out')

        framerate = float(video_caps[0]['framerate'])
        gobject.timeout_add(
            int(1000/framerate),
            lambda: self._need_video_data(appsrc, None))
        srcpad = appsrc.get_pad('src')
        srcpad.set_event_function(self._video_out_event)
        self._sync_state(bin)

    def set_keyboard_in(self, callback):
        self.keyboard_in = callback

    def set_mouse_in(self, callback):
        self.mouse_in = callback

    def _get_actual_audio_sink(self):
        audio_sink = self.pipeline.get_by_name('audio_sink')
        if audio_sink is None:
            return None

        if isinstance(audio_sink, gst.Bin):
            audio_sink = audio_sink.sinks().next()

        return audio_sink

    def _get_actual_video_sink(self):
        video_sink = self.pipeline.get_by_name('video_sink')

        if video_sink is None:
            return None

        if isinstance(video_sink, gst.Bin):
            video_sink = video_sink.sinks().next()

        return video_sink

    def _bus_message(self, bus, message):
        if message.type == gst.MESSAGE_ERROR:
            (gerror, err_str) = message.parse_error()

            if (self.exit_on_window_close and
                gerror.domain == gst.RESOURCE_ERROR and
                gerror.code == gst.RESOURCE_ERROR_NOT_FOUND and
                message.src == self._get_actual_video_sink()):
                self.loop.quit()
            else:
                print message

        return gst.BUS_PASS

    def _fps_timeout(self):
        now = time.time()

        if self.fps_timestamp is not None:
            t = now - self.fps_timestamp
            frames = self.frames_out - self.frames_out_prev
            text = self.pipeline.get_by_name('text')
            text.props.text = '%3.2f' % (frames / t)

        self.frames_out_prev = self.frames_out
        self.fps_timestamp = now
        return True

    def _terminal_input(self, _fd, _condition):
        c = os.read(0, 1)
        # XXX: We make no attempt here to handle non-trivial keys.
        # E.g. here backspace seems to get represented as '\x7f'
        # (ASCII DEL) and delete is the multi-byte sequence '\x1b[3~'.
        # ('\x1b[' is the ANSI CSI sequence.) To be consistent with
        # keyboard input under X, these would have to be mapped to
        # 'BackSpace' and 'Delete' respectively.
        self._keyboard_event('key-press', c)
        return True

    def _run_with_terminal_input(self):
        # XXX: Check that stdin is a terminal before attmepting to set
        # cbreak mode?
        t = numm.term.Terminal(0)
        gobject.io_add_watch(0, gobject.IO_IN, self._terminal_input)

        with t:
            t.set_cbreak()
            self.loop.run()

    def run(self):
        "Enter the mainloop."
        self.pipeline.set_state(gst.STATE_PLAYING)

        try:
            if self.keyboard_in is not None and self.video_out is None:
                # There is no input to receive keyoard input, so read
                # keyboard input from standard input instead.
                self._run_with_terminal_input()
            else:
                self.loop.run()
        finally:
            self.pipeline.set_state(gst.STATE_NULL)

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
            if self.keyboard_in(type, key):
                return

        if type == 'key-press':
            if key == 'F9':
                self.toggle_fps()
            elif key == 'F10':
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

    def toggle_fps(self):
        if self.fps_timeout_id is None:
            self.fps_timeout_id = gobject.timeout_add(1000, self._fps_timeout)
            self._fps_timeout()
        else:
            gobject.source_remove(self.fps_timeout_id)
            self.fps_timeout_id = None
            text = self.pipeline.get_by_name('text')
            text.props.text = ''

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


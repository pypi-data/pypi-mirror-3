
def test_run_video_in():
    r"""
    >>> import gobject
    >>> import gst

    >>> import numm

    >>> def video_in(a):
    ...     print 'video in', a.shape
    ...     loop.quit()

    >>> run = numm.Run(video_in=video_in, video_src='videotestsrc')
    >>> _ = run.pipeline.set_state(gst.STATE_PLAYING)
    >>> loop = gobject.MainLoop()
    >>> loop.run()
    video in (240, 320, 3)
    >>> run.pipeline.set_state(gst.STATE_NULL) == gst.STATE_CHANGE_SUCCESS
    True
    """

def test_run_video_out():
    r"""
    >>> import gobject
    >>> import gst

    >>> import numm
    >>> import numpy

    >>> def video_out(a):
    ...     a[:] = 42

    >>> def play():
    ...     run.pipeline.set_state(gst.STATE_PLAYING)

    >>> def buffer(sink, buf, pad):
    ...     a = numpy.fromstring(buf, numpy.uint8)
    ...     print a.shape
    ...     print a
    ...     loop.quit()

    >>> run = numm.Run(video_out=video_out, video_sink='fakesink')

    >>> fakesink = run.pipeline.get_by_name('video_sink')
    >>> fakesink.props.num_buffers = 1
    >>> fakesink.props.signal_handoffs = True
    >>> _ = fakesink.connect('handoff', buffer)

    >>> _ = gobject.idle_add(play)
    >>> loop = gobject.MainLoop()
    >>> loop.run()
    (230400,)
    [42 42 42 ..., 42 42 42]

    >>> run.pipeline.set_state(gst.STATE_NULL) == gst.STATE_CHANGE_SUCCESS
    True
    """

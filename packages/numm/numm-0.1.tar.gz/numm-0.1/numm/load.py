
import gobject
import gst

gobject.threads_init()

def _iter_pipeline(pipeline):
    context = gobject.main_context_default()
    error = []
    stop = [False]

    def message(bus, msg):
        if msg.type == gst.MESSAGE_ERROR:
            error.append(RuntimeError(msg))
            stop[0] = True
        elif msg.type == gst.MESSAGE_EOS:
            stop[0] = True

        return gst.BUS_PASS

    bus = pipeline.get_bus()
    bus.set_sync_handler(message)
    pipeline.set_state(gst.STATE_PLAYING)

    try:
        while not stop[0]:
            context.iteration()
            yield
    finally:
        ok = pipeline.set_state(gst.STATE_NULL)

        if ok != gst.STATE_CHANGE_SUCCESS:
            raise RuntimeError()

        state = pipeline.get_state()
        assert state[1] == gst.STATE_NULL, state

    if error:
        raise error[0]

def _loop_pipeline(pipeline):
    for _ in _iter_pipeline(pipeline):
        pass

def _run_appsink_pipeline(pipeline, appsink):
    ready = [0]

    def new_buffer(appsink):
        ready[0] += 1

    appsink.props.emit_signals = True
    appsink.props.sync = False
    appsink.connect('new-buffer', new_buffer)

    for _ in _iter_pipeline(pipeline):
        if appsink.props.eos:
            return

        for i in xrange(ready[0]):
            buf = appsink.emit('pull-buffer')

            if buf is not None:
                yield buf

        ready[0] = 0

def _run_appsrc_pipeline(pipeline, appsrc, get_chunk):
    position = [0]

    def need_data(src, length):
        try:
            (delta_p, a) = get_chunk(position[0], length)
        except IndexError:
            src.emit('end-of-stream')
            return

        if len(a) == 0:
            src.emit('end-of-stream')
            return

        src.emit('push-buffer', gst.Buffer(a.data))
        position[0] += delta_p

    appsrc.props.emit_signals = True
    appsrc.connect('need-data', need_data)
    _loop_pipeline(pipeline)

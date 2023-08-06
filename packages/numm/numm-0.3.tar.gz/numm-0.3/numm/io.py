
import threading

import gobject
import gst

gobject.threads_init()

class RunPipeline(object):
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.errors = []
        self.done = False
        self.context = gobject.main_context_default()

        bus = pipeline.get_bus()
        # Using a sync handler seems to deadlock with pulling a buffer.
        bus.add_watch(self._message)

    def _message(self, bus, msg):
        if msg.type == gst.MESSAGE_ERROR:
            self.errors.append(RuntimeError(msg))
            self.done = True
        elif msg.type == gst.MESSAGE_EOS:
            self.done = True

        return gst.BUS_PASS

    def start(self):
        self.pipeline.set_state(gst.STATE_PLAYING)

    def step(self):
        self.context.iteration()

    def stop(self):
        ok = self.pipeline.set_state(gst.STATE_NULL)

        if ok != gst.STATE_CHANGE_SUCCESS:
            raise RuntimeError()

        state = self.pipeline.get_state()
        assert state[1] == gst.STATE_NULL, state

    def run(self):
        try:
            self.start()

            while not self.done:
                yield self.step()
        finally:
            self.stop()

        if self.errors:
            raise self.errors[0]

class Reader(object):
    def __init__(self, pipeline, appsink):
        self.pipeline = pipeline
        self.appsink = appsink
        self._ready = threading.Semaphore(0)

        appsink.props.emit_signals = True
        appsink.props.max_buffers = 10
        appsink.props.sync = False
        appsink.connect('new-buffer', self._new_buffer)

    def _new_buffer(self, _appsink):
        # Wake up the mainloop so that the .iteration() call in
        # _iter_pipeline() returns. Otherwise we can be waiting
        # indefinitely.
        gobject.idle_add(lambda: False)

    def pull(self):
        return self.appsink.emit('pull-buffer')

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
    r = RunPipeline(pipeline)

    for _ in r.run():
        pass

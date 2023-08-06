
import sys
import traceback

import gio
import numm.async

def _load_module(path):
    source = file(path).read()
    code = compile(source, path, 'exec')
    globals_dict = {}
    exec code in globals_dict
    return globals_dict

def _monitor_changes(path, cb):
    def cb_(monitor, file, _other_file, event_type):
        if event_type == gio.FILE_MONITOR_EVENT_CHANGES_DONE_HINT:
            cb()

    monitor = gio.File(path).monitor()
    monitor.connect('changed', cb_)

def print_errors(f):
    def g(*a, **kw):
        try:
            f(*a, **kw)
        except Exception:
            traceback.print_exc()

    return g

def main():
    if len(sys.argv) < 2:
       raise RuntimeError()

    path = sys.argv[1]
    sys.argv[1:] = sys.argv[2:]
    run = numm.async.Run()

    def load():
        print 'load!'
        module = _load_module(path)

        for callback in numm.async.callbacks:
            f = module.get(callback) or module.get(callback + 'put')
            setter = getattr(run, 'set_' + callback, None)

            if f is not None:
                setter(print_errors(f))
            else:
                setter(None)

    load()
    _monitor_changes(path, load)
    run.run()


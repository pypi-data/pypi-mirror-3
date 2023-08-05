
import sys

import gio
import numpy
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

class FunctionProxy(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, *a, **kw):
        if self.func is  None:
            return

        try:
            self.func(*a, **kw)
        except Exception:
            import traceback
            traceback.print_exc()

    def __nonzero__(self):
        return self.func is not None

def main():
    if len(sys.argv) < 2:
       raise RuntimeError()

    path = sys.argv[1]
    sys.argv[1:] = sys.argv[2:]

    cb_args = {}

    for callback in numm.async.callbacks:
        cb_args[callback] = FunctionProxy(None)

    def load():
        print 'load!'
        module = _load_module(path)

        for callback in numm.async.callbacks:
            f = module.get(callback) or module.get(callback + 'put')
            cb_args[callback].func = f

    load()

    if not numpy.array(cb_args.values()).any():
        print 'no callbacks found'
        sys.exit(1)

    _monitor_changes(path, load)
    numm.async.run(**cb_args)

import gc

from ..Qt import QtCore, untrack_if_broken


class GarbageCollector(object):
    '''
    Disable automatic garbage collection and instead collect manually
    on a timer.

    This is done to ensure that garbage collection only happens in the GUI
    thread, as otherwise Qt can crash.

    Credit:  Erik Janssens
    Source:  http://pydev.blogspot.com/2014/03/should-python-garbage-collector-be.html
    '''

    def __init__(self, interval=1.0, debug=False):
        untrack_if_broken(self)
        self.debug = debug
        if debug:
            gc.set_debug(gc.DEBUG_LEAK)

        self.timer = QtCore.QTimer()
        untrack_if_broken(self.timer)
        self.timer.timeout.connect(self.check)

        self.threshold = gc.get_threshold()
        untrack_if_broken(self.threshold)
        gc.disable()
        self.timer.start(interval * 1000)

    def check(self):
        # Force disable GC in case it was re-enabled by another library
        if gc.isenabled():
            gc.disable()
            if self.debug:
                print('GC was re-enabled, disabling again')
        
        # Only perform manual collection if GC is disabled (intended use)
        if gc.isenabled():
            return
        counts = gc.get_count()
        if self.debug:
            print('gc_check called:', counts)
        
        try:
            if counts[2] > self.threshold[2]:
                if self.debug:
                    print('collecting gen 2...')
                num = gc.collect(2)
                if self.debug:
                    print('collected: %d unreachable' % num)
            elif counts[1] > self.threshold[1]:
                if self.debug:
                    print('collecting gen 1...')
                num = gc.collect(1)
                if self.debug:
                    print('collected: %d unreachable' % num)
            elif counts[0] > self.threshold[0]:
                if self.debug:
                    print('collecting gen 0...')
                num = gc.collect(0)
                if self.debug:
                    print('collected: %d unreachable' % num)
            
            # Clear the garbage list if any objects are stuck there
            if gc.garbage:
                if self.debug:
                    print('clearing gc.garbage (%d objects)' % len(gc.garbage))
                del gc.garbage[:]
        except Exception:
            if self.debug:
                import traceback
                traceback.print_exc()

    def debug_cycles(self):
        gc.collect()
        for obj in gc.garbage:
            print(obj, repr(obj), type(obj))

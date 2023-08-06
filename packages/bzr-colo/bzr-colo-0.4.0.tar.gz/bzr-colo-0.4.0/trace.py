from bzrlib import trace

DEBUG = True

def mutter(*args):
    if DEBUG:
        trace.mutter('bzr-colo: '+args[0], *args[1:])

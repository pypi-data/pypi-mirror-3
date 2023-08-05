
import os
import cPickle as pickle

def save(dir, subscribers):
    lock = FilesystemLock(dir + ".lock")
    if not lock.lock():
        raise SmapException("Could not acquire report file lock")
    
    try:
        if not os.path.isdir(dir):
            os.mkdir(dir)

    except (Exception):
        print "EH"
    finally:
        lock.unlock()

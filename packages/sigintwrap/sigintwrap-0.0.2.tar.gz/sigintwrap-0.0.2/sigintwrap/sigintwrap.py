#!/usr/bin/env python

import sys
import os
import signal

CHILD_PID = 0

def sig_forward(sig, frame):
    global CHILD_PID

    if CHILD_PID:
        print "forwarding sig: %i" % sig
        os.kill(CHILD_PID, sig)

def main():
    global CHILD_PID

    #install handlers
    signal.signal(signal.SIGINT, sig_forward)
    signal.signal(signal.SIGTERM, lambda sig, frame: sig_forward(signal.SIGINT, frame) )
    signal.signal(signal.SIGHUP, sig_forward)
    signal.signal(signal.SIGQUIT, sig_forward)
    signal.signal(signal.SIGUSR1, sig_forward)
    signal.signal(signal.SIGUSR2, sig_forward)
    signal.signal(signal.SIGPIPE, sig_forward)
    signal.signal(signal.SIGALRM, sig_forward)

    CHILD_PID = os.fork()

    if CHILD_PID > 0:
        # wait for our children ... this should be only 1
        while True:
            try:
                pid, status = os.wait()
                if pid != CHILD_PID:
                    print "Unspawned child process returned!"
                return status
            except OSError as e:
                if e.errno == os.errno.EINTR:
                    # call was interrupted do to signal forwarding
                    pass
                else:
                    print "Exited due to: %s" % repr(e)
                    return -1
            except Exception as e:
                print "Exited due to: %s" % repr(e)
                return -1

    else:
        os.execve(sys.argv[1], sys.argv[1:], os.environ)
        print "Failed to exec!"
        return -1

if __name__ == "__main__":
    sys.exit(main())


"""
Simple implementation of a unix daemon process.
For testign purposes only.
"""

import daemon
import sys
from lockfile.pidlockfile import PIDLockFile
from time import sleep

def main():
    if len(sys.argv) == 2:
        pid_file_path = sys.argv[1] # get pid file path per command line arg
    else :
        pid_file_path = '/tmp/dummy_daemon.pid'
    pidfile = PIDLockFile(pid_file_path) # create a PIDLockFile instance
    context = daemon.DaemonContext(pidfile=pidfile) # create an deaemon contex 
    with context:
        while True: # do sleep forever
            sleep(1)

if __name__ == "__main__":
    main()


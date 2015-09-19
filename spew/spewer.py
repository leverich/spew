import json
import os
import time
import zlib

class Spewer:
    interval = 1.0
    files = []
    logfile = None
    pidpath = None

    def __init__(self, interval = 1.0, logpath_prefix = None):
        if interval and interval > 0 and interval <= 3600:
            self.interval = interval

        log_suffix = "spew.%s" % (os.uname()[1])

        if not logpath_prefix: logpath = log_suffix
        else: logpath = logpath_prefix + "/" + log_suffix

        pidpath = logpath + ".pid"

        # Check for pid file, make sure the process isn't running.
        pidfile = None
        try:
            pidfile = open(pidpath, "r")
            if pidfile:
                pid = int(pidfile.readline().strip())
                if not os.kill(pid, 0):  # Process is still running.
                    raise Exception("Logfile is locked by pid " + str(pid))
        except IOError: pass  # No pid file.
        except ValueError: pass  # Couldn't parse pid file.
        except OSError: pass  # Process isn't running.
        finally:
            if pidfile: pidfile.close()

        # Create a pidfile and open logfile for append.
        self.pidpath = pidpath  # For our destructor.
        pidfile = open(pidpath, "w")
        pidfile.write(str(os.getpid()) + "\n")
        pidfile.close()

        self.logfile = open(logpath, "a")

        # Register default files to spew.
        self.add_file("/proc/stat")
        self.add_file("/proc/diskstats")
        self.add_file("/proc/net/dev")

    def __del__(self):
        try: os.unlink(self.pidpath)
        except: pass

    def add_file(self, filename):
        if not os.path.isfile(filename):
            raise IOError(filename + " not found")

        self.files.append(filename)

    def log(self):
        timestamp = time.time()

        filedump = {}

        for filename in self.files:
            f = open(filename)
            filedump[filename] = "".join(f.readlines())
            f.close()

        dumpstring = json.dumps(filedump)
        self.logfile.write("%f %s\n" % (timestamp, dumpstring))

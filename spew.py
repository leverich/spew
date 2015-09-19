#!/usr/bin/python

from optparse import OptionParser
import os
import select
import signal
import time

from spew import spewer

def sigterm_handler(signum, frame):
    raise Exception("SIGTERM!")

if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option("-d", "--duration", dest="duration",
                      default=86400, type="int",
                      help="maximum duration to log", metavar="SECONDS")
    parser.add_option("-i", "--interval", dest="interval",
                      default=1.0, type="float",
                      help="report interval (float)", metavar="SECONDS")
    parser.add_option("-p", "--logpath", dest="logpath",
                      default = None, type="str",
                      help="Path of directory in which to store logs",
                      metavar="DIR")
    parser.add_option("-c", "--cgroup", dest="cgs", action="append",
                      default = [], type="str",
                      help="Name of cgroup to monitor", metavar="CGROUP")

    (options, args) = parser.parse_args()

    spewer = spewer.Spewer(logpath_prefix = options.logpath,
                           interval = options.interval)

    for cg in options.cgs:
        spewer.add_file("/sys/fs/cgroup/memory/%s/memory.stat" % cg)
        spewer.add_file("/sys/fs/cgroup/memory/%s/memory.limit_in_bytes" % cg)
        spewer.add_file("/sys/fs/cgroup/memory/%s/memory.soft_limit_in_bytes" %
                        cg)
        spewer.add_file("/sys/fs/cgroup/memory/%s/memory.memsw.limit_in_bytes" % 
                        cg)
        spewer.add_file("/sys/fs/cgroup/memory/%s/memory.max_usage_in_bytes" %
                        cg)
        spewer.add_file(("/sys/fs/cgroup/memory/%s/" +
                        "memory.memsw.max_usage_in_bytes") % cg)
        spewer.add_file("/sys/fs/cgroup/cpuacct/%s/cpuacct.stat" % cg)
        spewer.add_file("/sys/fs/cgroup/cpuacct/%s/cpuacct.usage" % cg)

    signal.signal(signal.SIGTERM, sigterm_handler)

    poll = select.poll()

    now = time.time()
    start_time = now
    next_time = now + options.interval

    while now < start_time + options.duration:
        now = time.time()
        spewer.log()

        while next_time <= now: next_time += options.interval

        try: poll.poll((next_time - now) * 1000.0)
        except Exception as e:
            print e
            break

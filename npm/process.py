from __future__ import print_function

import sys
import threading


class StdinWriter(threading.Thread):
    """Reads stdin data and passes back to the process"""
    def __init__(self, proc):
        threading.Thread.__init__(self)
        self.proc = proc
        self.setDaemon(True)

    def do_input(self):
        data = sys.stdin.readline()
        self.proc.stdin.write(data)
        self.proc.stdin.flush()

    def run(self):
        while self.proc.poll() is None:
            try:
                self.do_input()
            except (IOError, ValueError):
                break

    def close(self):
        self.proc.stdin.close()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

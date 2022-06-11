import threading
import time

def do(i=None):
    print(i)

def run():
    t = threading.current_thread()
    i = 0
    while True:
        if not getattr(t, "do_run", True):
            return
        i= i+ 1
        do(i)
        time.sleep(10)
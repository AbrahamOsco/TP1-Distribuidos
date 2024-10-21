import multiprocessing
import logging

class GlobalCounter:
    _counter = multiprocessing.Value('i', 1)
    _lock = multiprocessing.Lock()  # Protects the singleton creation

    def get_next():
        with GlobalCounter._lock:
            value = GlobalCounter._counter.value
            GlobalCounter._counter.value += 1
        return value
import multiprocessing

class GlobalCounter:
    _counter = multiprocessing.Value('i', 1)
    _lock = multiprocessing.Lock()  # Protects the singleton creation

    def get_next():
        with GlobalCounter._lock:
            value = GlobalCounter._counter.value
            GlobalCounter._counter.value += 1
        return value
    
    def set_current(value):
        with GlobalCounter._lock:
            GlobalCounter._counter.value = value
    
    def get_current():
        with GlobalCounter._lock:
            return GlobalCounter._counter.value
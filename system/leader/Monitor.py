import threading

class Monitor:
    def __init__(self, value):
        self.value = value
        self.lock = threading.Lock()

    def is_this_value(self, value):
        with self.lock:
            return self.value == value
    
    def set_value(self, value = None):
        with self.lock:
                self.value = value
    def get_value(self):
        with self.lock:
            return self.value
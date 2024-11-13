import threading

class ControlValue():
    def __init__(self, value):
        self.value = value
        self.lock = threading.Lock()
        self.condition = threading.Condition()
    
    def change_value(self, new_value):
        with self.lock:
            self.value = new_value
    
    def notify_all(self):
        with self.condition:
            self.condition.notify_all()
    
    def is_this_value(self, a_value):
        with self.lock:
            return self.value == a_value


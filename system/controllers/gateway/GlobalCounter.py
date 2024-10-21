import multiprocessing
import logging

class GlobalCounter:
    _counter = multiprocessing.Value('i', 1)
    _lock = multiprocessing.Lock()  # Protects the singleton creation

    def get_next():
        logging.info("Llegue 10")
        with GlobalCounter._lock:
            logging.info("Llegue 11")
            value = GlobalCounter._counter.value
            logging.info("Llegue 12")
            GlobalCounter._counter.value += 1
        return value
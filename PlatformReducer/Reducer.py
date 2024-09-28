import logging
import os

class Reducer:
    def __init__(self):
        self.initialize_config()
        self.running = True
        self.reset_counter()

    def reset_counter(self):
        self.result = {
            "windows": 0,
            "linux": 0,
            "mac": 0,
        }

    def initialize_config(self):
        self.config_params = {}
        self.config_params["id"] = int(os.getenv("CLI_ID"))
        self.config_params["log_level"] = os.getenv("CLI_LOG_LEVEL")
        self.initialize_log()


    def initialize_log(self):
        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=self.config_params["log_level"],
            datefmt='%Y-%m-%d %H:%M:%S',
        )

    def receive_data(self):
        data = []
        return data
    
    def is_eof(self, data):
        return data == "EOF"
    
    def send_result(self):
        logging.info(f"action: result | windows: {self.result['windows']} | linux: {self.result['linux']} | mac: {self.result['mac']}")

    def process_data(self, data):
        if self.is_eof(data):
            self.send_result()
            self.reset_counter()
            return
        for d in data:
            self.result["windows"] += d["windows"]
            self.result["linux"] += d["linux"]
            self.result["mac"] += d["mac"]

    def run(self):
        while self.running:
            try:
                data = self.receive_data()
                self.process_data(data)
            except Exception as e:
                logging.error(f"action: error | result: {e}")
    
    def stop(self):
        self.running = False

    
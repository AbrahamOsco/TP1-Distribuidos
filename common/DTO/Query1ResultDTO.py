OPERATION_TYPE_QUERY1 = 1

import logging
class Query1ResultDTO:
    def __init__(self, windows, linux, mac):
        self.operation_type = OPERATION_TYPE_QUERY1
        self.query = 1
        self.windows = windows
        self.linux = linux
        self.mac = mac
    
    def print(self):
        logging.info("Result Query 1")
        logging.info(f"windows: {self.windows}")
        logging.info(f"linux: {self.linux}")
        logging.info(f"mac: {self.mac}")
        logging.info("")

    def append_data(self, responses):
        responses["Query1"] = {"windows": self.windows, "linux": self.linux, "mac": self.mac}
        return responses
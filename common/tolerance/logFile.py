import os
import logging

FILE_PATH = "/persistent/"

class LogFile:
    def __init__(self, identifier: str):
        self.file_name = FILE_PATH + identifier + "logs"
        self.logs = []
        self.log_count = 0
        self._load_file()
        self._init_file_write()

    def is_full(self):
        return self.log_count >= 100

    def _init_file_write(self):
        self.file = open(self.file_name, "ab")

    def _load_file(self):
        try:
            file = open(self.file_name, "rb")
            data = file.read()
            file.close()
            self.logs = self._parse_logs(data)
            self._truncate_to_last_uncorrupted(self.file_name)
        except FileNotFoundError:
            self.logs = b""

    def _parse_logs(self, data: bytes):
        if len(data) == 0:
            logging.info("Empty log file")
            return []
        logs = []
        offset = 0
        while len(data[offset:]) >= 6:
            log_size = int.from_bytes(data[offset:offset+6], "big")
            offset += 6
            if len(data[offset:]) < log_size + 1:
                return logs
            log = data[offset:offset+log_size]
            offset += log_size
            if data[offset:offset+1] != b"\n":
                return logs
            offset += 1
            logs.append(log)
        return logs
    
    def _remove_file(self):
        try:
            os.remove(self.file_name)
        except FileNotFoundError:
            pass

    def _truncate_to_last_uncorrupted(self, file_path: str):
        temp_file_path = file_path + ".tmp"

        with open(temp_file_path, "wb") as temp_file:
            for log in self.logs:
                self._add_log_to_file(log, temp_file)

        os.replace(temp_file_path, file_path)

    def get_next_log(self):
        if len(self.logs) == 0:
            return None
        return self.logs.pop(0)
    
    def reset(self):
        self.file.close()
        self.logs = []
        self.log_count = 0
        self._remove_file()
        self._init_file_write()
    
    def add_log(self, content: bytes):
        self._add_log_to_file(content, self.file)
        self.log_count += 1

    def _add_log_to_file(self, content: bytes, file):
        file.write(len(content).to_bytes(6, "big"))
        file.write(content + b"\n")
        file.flush()
        os.fsync(file.fileno())
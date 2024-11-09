import os

FILE_PATH = "/persistent/logs"

class LogFile:
    def __init__(self):
        self.logs = []
        self._load_file(FILE_PATH)
        self._init_file_write()

    def _init_file_write(self):
        self.file = open(FILE_PATH, "ab")

    def _load_file(self):
        try:
            file = open(FILE_PATH, "rb")
            data = file.read()
            file.close()
            self.logs = self._parse_logs(data)
            self._truncate_to_last_uncorrupted(FILE_PATH)
        except FileNotFoundError:
            self.logs = b""

    def _parse_logs(self, data: bytes):
        split_data = data.split(b"\n")
        logs = []
        for i in range(0, len(split_data) - 1, 2):
            log = split_data[i]
            status = split_data[i + 1]
            
            # Check if the current log has 'UNCORRUPTED' following it
            if status == b"UNCORRUPTED":
                logs.append(log.decode())
        
        return logs
    
    def _remove_file(self):
        try:
            os.remove(FILE_PATH)
        except FileNotFoundError:
            pass

    def _truncate_to_last_uncorrupted(self, file_path: str):
        marker = b"UNCORRUPTED\n"
        marker_len = len(marker)
        temp_file_path = file_path + ".tmp"
        last_position = None

        # Step 1: Check if the file already ends with 'UNCORRUPTED\n'
        with open(file_path, "rb") as file:
            file.seek(-marker_len, os.SEEK_END)  # Move to the last part of the file
            if file.read(marker_len) == marker:
                print("File already ends with 'UNCORRUPTED'. No action taken.")
                return  # File ends with 'UNCORRUPTED', so no need to truncate
            
        # Step 1: Find the last occurrence of 'UNCORRUPTED\n' and record the position
        with open(file_path, "rb") as file:
            offset = 0
            while True:
                chunk = file.read(4096)  # Read in chunks for large files
                if not chunk:
                    break

                position = chunk.rfind(marker)
                if position != -1:
                    last_position = offset + position + len(marker)

                offset += len(chunk)

        # If no 'UNCORRUPTED\n' was found, do nothing
        if last_position is None:
            print("No 'UNCORRUPTED' marker found. File remains unchanged.")
            self._remove_file()
            return

        with open(file_path, "rb") as original_file, open(temp_file_path, "wb") as temp_file:
            temp_file.write(original_file.read(last_position))

        os.replace(temp_file_path, file_path)

    def get_next_log(self):
        if len(self.logs) == 0:
            return None
        return self.logs.pop(0)
    
    def reset(self):
        self.file.close()
        self.logs = []
        self._remove_file()
        self._init_file_write()
    
    def add_log(self, content: bytes):
        self.file.write(content + b"\nUNCORRUPTED\n")
        self.file.flush()
        os.fsync(self.file.fileno())
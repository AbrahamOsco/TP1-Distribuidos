import os
import csv
import sys
import logging
INDEX_TO_FIX_HEADER = 7
PERCENT_OF_FILE_FOR_USE = 0.1

class FileReader:
    def __init__(self, file_name, batch_size):
        FILE_PATHS = {"games": "./data/games.csv", "reviews": "./data/dataset.csv" }
        csv.field_size_limit(sys.maxsize)
        self.file_name = file_name
        self.batch_size = batch_size
        self.file =  open(FILE_PATHS[file_name], mode ="r", newline ="", encoding ="utf-8")
        self.reader = csv.reader(self.file)
        self.usage_limit = PERCENT_OF_FILE_FOR_USE * os.path.getsize(FILE_PATHS[file_name])
        self.bytes_read = 0
        self.is_closed = False
        self.last_read = None
        next(self.reader) # skip header

    def get_next_batch(self):
        games = []
        if(self.is_closed):
            logging.info(f"action: get_next_batch | result: sucess | event: There's not more '{self.file_name}' to send! 💯")
            return None
        try:
            current_size = 0
            if self.last_read is not None:
                games.append(self.last_read)
                total_size_raw = sum(len(element) for element in self.last_read)
                self.bytes_read += (total_size_raw + len(self.last_read))
                current_size += total_size_raw
                self.last_read = None
            for _ in range(self.batch_size):
                if self.bytes_read > self.usage_limit:
                    self.close()
                    break
                data_raw = next(self.reader)
                total_size_raw = sum(len(element) for element in data_raw)
                if current_size + total_size_raw > 2**24:
                    self.last_read = data_raw
                    break
                self.bytes_read += (total_size_raw + len(data_raw))
                current_size += total_size_raw
                games.append(data_raw)
        except StopIteration:
            self.close()
        return games

    def close(self):
         if not self.is_closed:
            self.file.close()
            self.is_closed = True
            logging.info(f"action: 👉file_associated_with_{self.file_name}_is_closed | result: sucess | file closed : {self.is_closed} 🆓")

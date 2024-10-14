import os
import csv
import sys
import logging
PERCENT_OF_FILE_FOR_USE = 1

class FileReader:
    def __init__(self, file_name, batch_size=25, percent_of_file_for_use:float=PERCENT_OF_FILE_FOR_USE):
        FILE_PATHS = {"games": "./data/games.csv", "reviews": "./data/dataset.csv" }
        csv.field_size_limit(sys.maxsize)
        self.file_name = file_name
        self.batch_size = batch_size
        self.file_path = FILE_PATHS[file_name]
        self.usage_limit = percent_of_file_for_use * os.path.getsize(self.file_path)
        self.file =  open(self.file_path, mode ="r", newline ="", encoding ="utf-8")
        self.reader = csv.reader(self.file)
        self.bytes_read = 0
        self.is_closed = False
        next(self.reader)
        self.lines_read = 0

    def get_next_batch(self):
        data_read = []
        if(self.is_closed):
            logging.info(f"action: get_next_batch | event: Closed the file '{self.file_name}' | result: sucess ✅ |")
            return None
        try:
            current_size = 0
            for _ in range(self.batch_size): 
                if self.bytes_read > self.usage_limit:
                    self.close()
                    break
                data_raw = next(self.reader) 
                self.lines_read += 1
                total_size_raw = sum(len(element) for element in data_raw)
                self.bytes_read += (total_size_raw + len(data_raw)) 
                current_size += total_size_raw
                data_read.append(data_raw)
        except StopIteration:
            self.close()
        return data_read

    def get_lines_read(self):
        return self.lines_read

    def close(self):
         if not self.is_closed:
            self.file.close()
            self.is_closed = True
            logging.info(f"action: File associated with {self.file_name} is closed | file closed : {self.is_closed} 🆓 | result: sucess ✅")
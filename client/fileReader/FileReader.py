import os
import csv
import logging
import math
INDEX_TO_FIX_HEADER = 7
MAX_FIELD_SIZE_CSV = 1000000000

class FileReader:
    def __init__(self, file_name, batch_size, percent_of_file_for_use):
        csv.field_size_limit(MAX_FIELD_SIZE_CSV)
        FILE_PATHS = {"games": "./data/games.csv", "reviews": "./data/dataset.csv" }
        self.file_name = file_name
        self.percent_of_file_for_use = percent_of_file_for_use
        self.batch_size = batch_size
        self.file =  open(FILE_PATHS[file_name], mode ="r", newline ="", encoding ="utf-8")
        self.reader = csv.reader(self.file)
        self.usage_limit = self.percent_of_file_for_use * os.path.getsize(FILE_PATHS[file_name])
        self.bytes_read = 0
        self.is_closed = False
        self.fix_header_game = False
        self.read_all = False
        self.amount_data = -1 # header no cuenta. 
    def read_all_data(self):
        return self.read_all

    def get_next_batch(self):
        games = []
        if(self.is_closed):
            logging.info(f"action: get next batch | event: File '{self.file_name}' is closed | result: sucess ✅")
            return None
        try:
            for _ in range(self.batch_size):
                if self.bytes_read > self.usage_limit:
                    self.read_all = True
                    self.close()
                    break
                data_raw = next(self.reader)
                self.amount_data +=1
                total_size_raw = 0 
                for element in data_raw:
                    total_size_raw += len(element)
                self.bytes_read += (total_size_raw + len(data_raw)) # Sumo bytes de cada elemento de la lista, comas y \n.
                if self.fix_header_game == False and self.file_name == 'games':
                    data_raw.insert(INDEX_TO_FIX_HEADER, 'Unknown') # add a new column to synchronize the header
                    self.fix_header_game = True
                games.append(data_raw)
        except StopIteration:
            self.close()
            self.read_all = True
        return games

    def close(self):
         if not self.is_closed:
            self.file.close()
            self.is_closed = True
            logging.info(f"action: 👉File associated with {self.file_name} is closed | result: sucess | file closed : {self.is_closed} 🆓")

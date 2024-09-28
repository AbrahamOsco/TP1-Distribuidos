import os
import csv
import logging
INDEX_TO_FIX_HEADER = 7
PERCENT_OF_FILE_FOR_USE = 0.10

class FileReader:
    def __init__(self, file_name, batch_size):
        FILE_PATHS = {"games": "./data/games.csv", "reviews": "./data/dataset.csv" }
        self.file_name = file_name
        self.batch_size = batch_size
        self.file =  open(FILE_PATHS[file_name], mode ="r", newline ="", encoding ="utf-8")
        self.reader = csv.reader(self.file)
        self.usage_limit = PERCENT_OF_FILE_FOR_USE * os.path.getsize(FILE_PATHS[file_name])
        self.bytes_read = 0
        self.is_closed = False
        self.fix_header_game = False

    def get_next_batch(self):
        games = []
        if(self.is_closed):
            logging.info(f"action: get_next_batch | result: sucess | event: There's not more '{self.file_name}' to send! 💯")
            return None
        try:
            for _ in range(self.batch_size):
                if self.bytes_read > self.usage_limit:
                    self.close()
                    break
                game_raw = next(self.reader) #retorn a list of string
                self.bytes_read += sum( len(cell) for cell in game_raw ) +1 # +1 for each comma or \n.
                if self.fix_header_game == False and self.file_name == 'games':
                    game_raw.insert(INDEX_TO_FIX_HEADER, 'unknown') # add a new column to synchronize the header
                    self.fix_header_game = True
                games.append(game_raw)
        except StopIteration:
            self.close()
        return games

    def close(self):
         if not self.is_closed:
            self.file.close()
            self.is_closed = True
            logging.info(f"action: 👉file_associated_with_{self.file_name}_is_closed | result: sucess | file closed : {self.is_closed} 🆓")

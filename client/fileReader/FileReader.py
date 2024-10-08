import os
import csv
import sys
import logging

INDEX_TO_FIX_HEADER = 7
ELEMENTS_TO_USE = 5  # Limitar a 5 elementos

class FileReader:
    def __init__(self, file_name, batch_size):
        FILE_PATHS = {"games": "./data/games.csv", "reviews": "./data/dataset.csv"}
        csv.field_size_limit(sys.maxsize)
        self.file_name = file_name
        self.batch_size = batch_size
        self.file = open(FILE_PATHS[file_name], mode="r", newline="", encoding="utf-8")
        self.reader = csv.reader(self.file)
        self.elements_read = 0  # Para contar los elementos leídos
        self.is_closed = False
        self.last_read = None
        next(self.reader)  # Saltar encabezado

    def get_next_batch(self):
        games = []
        if self.is_closed:
            logging.info(f"action: get_next_batch | result: success | event: There's no more '{self.file_name}' to send! 💯")
            return None
        try:
            if self.last_read is not None:
                games.append(self.last_read)
                self.elements_read += 1
                self.last_read = None
            for _ in range(self.batch_size):
                if self.elements_read >= ELEMENTS_TO_USE:
                    self.close()
                    break
                data_raw = next(self.reader)
                games.append(data_raw)
                self.elements_read += 1
        except StopIteration:
            self.close()
        return games

    def close(self):
        if not self.is_closed:
            self.file.close()
            self.is_closed = True
            logging.info(f"action: 👉file_associated_with_{self.file_name}_is_closed | result: success | file closed : {self.is_closed} 🆓")

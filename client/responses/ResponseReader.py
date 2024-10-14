import csv
import os
import logging

FilesPrefixesResponse = {
    0.1: "1",
    0.2: "2",
    0.3: "3",
    0.4: "4",
    0.5: "5",
    1: ""
}

class ResponseReader:

    def __init__(self, query_name, percent_of_file):
        self.file_path = "./data/responses/"
        self.file_path += FilesPrefixesResponse[percent_of_file]
        self.file_path += query_name + ".csv"
        self.file =  open(self.file_path, mode ="r", newline ="", encoding ="utf-8")
        self.reader = csv.reader(self.file)
        self.is_closed = False

    def get_next_line(self):
        if(self.is_closed):
            logging.info(f"action: get next line | event: There's not more '{self.file_path}' to compare | sucess: ✅")
            return None
        try:
            return next(self.reader)
        except StopIteration:
            self.close()
            return None

    def close(self):
     if not self.is_closed:
        self.file.close()
        self.is_closed = True
        logging.info(f"action: Query Response File {self.file_path} is closed | file closed : {self.is_closed} 🆓| result: sucess ✅")
    
    
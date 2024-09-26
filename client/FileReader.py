import csv
import logging
BATCH_SIZE = 50
SEPARATOR = ","

class FileReader:
    def __init__(self, file_name ='games',  batch_size =BATCH_SIZE ):
        FILE_PATHS = {"games": "./data/games/games.csv", "reviews": "./data/reviews/dataset.csv" }
        self.file_name = file_name
        self.batch_size = batch_size
        self.file =  open(FILE_PATHS[file_name], mode ="r", newline ="", encoding ="utf-8") 
        self.reader = csv.reader(self.file)
        self.is_closed = False

    def get_next_batch(self):
        games = []
        if(self.is_closed):
            logging.info(f"action: get_next_batch | result: sucess | event: There's not more '{self.file_name}' to send! 💯")
            return None
        try:
            for _ in range(self.batch_size):
                game_raw = next(self.reader)
                print(game_raw)
                games.append(SEPARATOR.join(game_raw))
        except StopIteration:
            self.close()
        return games

    def close(self):
         if not self.is_closed:
            self.file.close()
            self.is_closed = True
            logging.info(f"action: 👉file_associated_with_{self.file_name}_is_closed | result: sucess | file closed : {self.is_closed} 🆓")

"""
from common.DTO.GameDTO import GameDTO
    def initialize_position_dic(self):
        self.pos = {"AppID": 0 , "Name": 0, "Windows": 0, "Mac": 0, "Linux": 0,\
            "Genres": 0, "Release date": 0, "Average playtime forever": 0}
        header = next(self.reader)
        for i, element in enumerate(header):
            if element in self.pos.keys():
                self.pos[element] = i 
        in next_batch: 
        game_dto = GameDTO(app_id =line[self.pos['AppID']], name =line[self.pos['Name']], windows =line[self.pos['Windows']], \
            linux =line[self.pos['Linux']], genres =self.pos['Genres'], release_date =self.pos['Release date'], \
            avg_playtime_forever =self.pos['Average playtime forever'])
"""
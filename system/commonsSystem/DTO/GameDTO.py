OPERATION_TYPE_GAME = 1
INITIAL_GAME = 1

class GameDTO:
    def __init__(self, status = INITIAL_GAME, app_id ="", name ="", windows ="",\
            mac ="", linux ="", genres ="", release_date ="", avg_playtime_forever =""):
        self.operation_type = 1
        self.status = status
        self.app_id = int(app_id)
        self.name = name
        self.windows = windows
        self.mac = mac
        self.linux = linux
        self.genres = genres
        self.release_date = release_date
        self.avg_playtime_forever = avg_playtime_forever
        

    def print_game_in_one_line(self):
        print("Game: ", self.app_id, self.name, self.windows, self.mac, self.linux, self.genres, self.release_date, self.avg_playtime_forever)
    
    def is_EOF(self):
        return True
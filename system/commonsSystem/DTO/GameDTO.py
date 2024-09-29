OPERATION_TYPE_GAME = 1
INITIAL_GAME = 1

class GameDTO:
    def __init__(self, status = INITIAL_GAME, app_id ="", client ="", name ="", windows ="",\
            mac ="", linux ="", genres ="", release_date ="", avg_playtime_forever =""):
        self.operation_type = 1
        self.status = status
        self.client = client
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
    
    def to_string(self):
        return f"GAME|{self.app_id}|{self.client}|{self.name}|{self.windows}|{self.mac}|{self.linux}|{self.genres}|{self.release_date}|{self.avg_playtime_forever}"

    def from_string(data):
        data = data.split("|")
        return GameDTO(data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9])

    def is_EOF(self):
        return False
    
    def get_client(self):
        return self.client
    
    def retain(self, fields_to_keep):
        attributes = vars(self)
        for attr in list(attributes.keys()):
            if attr not in fields_to_keep:
                setattr(self, attr, None)
        return self
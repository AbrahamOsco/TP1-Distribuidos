import logging
OPERATION_TYPE_GAME = 1

class GameDTO:
    def __init__(self, app_id ="", client_id =0, name ="", windows =0,\
            mac =0, linux =0, genres ="", release_date ="", avg_playtime_forever =""):
        self.operation_type = OPERATION_TYPE_GAME
        self.client_id = client_id # es enviado pero lo saco de una si no se usa. 
        self.app_id = app_id
        self.name = name
        self.release_date = release_date
        self.windows = int(windows)
        self.mac = int(mac)
        self.linux = int(linux)
        self.avg_playtime_forever = avg_playtime_forever
        self.genres = genres


    def show_game(self):
        logging.info(f"action: Show Game: {self.app_id}, {self.name}, {self.windows}, {self.mac}, {self.linux}, {self.genres}, {self.release_date}, {self.avg_playtime_forever}")
    
    def to_string(self):
        return f"GAME|;|{self.app_id}|;|{self.client_id}|;|{self.name}|;|{self.windows}|;|{self.mac}|;|{self.linux}|;|{self.genres}|;|{self.release_date}|;|{self.avg_playtime_forever}"

    def from_string(data):
        data = data.split("|;|")
        return GameDTO(data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9])

    def is_EOF(self):
        return False
    
    def get_client(self):
        return self.client_id
    
    def retain(self, fields_to_keep):
        attributes = vars(self)
        for attr in list(attributes.keys()):
            if attr not in fields_to_keep:
                setattr(self, attr, None)
        return self
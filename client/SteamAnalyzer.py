from client.FileReader import FileReader
from common.socket.Socket import Socket
from client.ClientProtocol import ClientProtocol

class SteamAnalyzer:
    def __init__(self):
        self.game_reader = FileReader(file_name='games', batch_size=4)
        self.review_reader = FileReader(file_name='reviews', batch_size=5)
        self.socket = Socket("127.0.0.1", 8081)
        self.socket.connect()
        self.protocol = ClientProtocol(self.socket)
        self.start()

    def start(self):
        # send 3 batch of game (take care i sent the header too! )
        for i in range(3):
            some_games = self.game_reader.get_next_batch()
            self.protocol.send_data_raw(some_games)
        
        # send 3 batch of review (take care i sent the header too! ) 
        for j in range(3):
            some_reviews = self.review_reader.get_next_batch()
            self.protocol.send_data_raw(some_reviews)
            print("END a batch | 🔥")

    def get_result_from_queries(self):
        print("in process ⌚s")
        pass

    
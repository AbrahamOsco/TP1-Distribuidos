import os
import logging
from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_IDNAME
from system.commonsSystem.node.IDList import IDList
from common.tolerance.logFile import LogFile

class GrouperNode(Node):
    def __init__(self, incoming_state, query, comparing_field):
        super().__init__()
        self.reset_list()
        self.top_size = int(os.getenv("TOP_SIZE"))
        self.incoming_state = incoming_state
        self.query = query
        self.comparing_field = comparing_field
        self.id_list = IDList()
        self.logs = LogFile()

    def reset_list(self, client_id=None):
        if client_id is None:
            self.list = {}
            self.min_time = {}
            self.counters = {}
        else:
            del self.list[client_id]
            del self.min_time[client_id]
            del self.counters[client_id]

    def pre_eof_actions(self, client_id):
        if client_id not in self.list:
            return
        games = GamesDTO(client_id=client_id, state_games=self.incoming_state, games_dto=self.list[client_id], query=self.query, global_counter=self.counters[client_id])
        games.set_state(STATE_IDNAME)
        self.send_result(games)
        self.reset_list(client_id)

    def has_to_be_inserted(self, game, current_client):
        return len(self.list[current_client]) < self.top_size or game.get(self.comparing_field) > self.min_time[current_client]
    
    def send_result(self, games):
        self.broker.public_message(sink=self.sink, message=games.serialize(), routing_key="default")

    def process_data(self, data: GamesDTO):
        if self.id_list.already_processed(data.global_counter):
            logging.info(f"Already processed {data.global_counter}")
            return
        current_client = data.get_client()
        if current_client not in self.list:
            self.list[current_client] = []
            self.min_time[current_client] = 0
        self.id_list.insert(data.global_counter)
        self.logs.add_log(data.serialize())
        self.counters[current_client] = data.global_counter
        for game in data.games_dto:
            if self.has_to_be_inserted(game, current_client):
                inserted = False
                for i in range(len(self.list[current_client])):
                    if game.get(self.comparing_field) > self.list[current_client][i].get(self.comparing_field):
                        self.list[current_client].insert(i, game)
                        inserted = True
                        break
                if not inserted:
                    self.list[current_client].append(game)
                if len(self.list[current_client]) > self.top_size:
                    self.list[current_client].pop()
                self.min_time[current_client] = self.list[current_client][-1].get(self.comparing_field)
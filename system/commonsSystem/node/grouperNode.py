import os
import logging
from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_IDNAME
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.node.IDList import IDList
from common.tolerance.logFile import LogFile
from system.commonsSystem.node.structures.grouperStructure import GrouperStructure
from common.tolerance.checkpointFile import CheckpointFile

class GrouperNode(Node):
    def __init__(self, incoming_state, query, comparing_field):
        super().__init__()
        self.top_size = int(os.getenv("TOP_SIZE"))
        self.incoming_state = incoming_state
        self.query = query
        self.comparing_field = comparing_field
        self.id_list = IDList()
        self.logs = LogFile()
        self.checkpoint = CheckpointFile()
        self.data = GrouperStructure(self.incoming_state)
        self.recover()

    def pre_eof_actions(self, client_id):
        if client_id not in self.data.list:
            return
        games = GamesDTO(client_id=client_id, state_games=self.incoming_state, games_dto=self.data.list[client_id], query=self.query, global_counter=self.data.counters[client_id])
        games.set_state(STATE_IDNAME)
        self.send_result(games)
        self.data.reset(client_id)

    def has_to_be_inserted(self, game, current_client):
        return len(self.data.list[current_client]) < self.top_size or game.get(self.comparing_field) > self.data.min_time[current_client]
    
    def send_result(self, games):
        self.broker.public_message(sink=self.sink, message=games.serialize(), routing_key="default")

    def process_data(self, data: GamesDTO):
        if self.id_list.already_processed(data.global_counter):
            logging.info(f"Already processed {data.global_counter}")
            return
        current_client = data.get_client()
        if current_client not in self.data.list:
            self.data.list[current_client] = []
            self.data.min_time[current_client] = 0
        self.id_list.insert(data.global_counter)
        self.logs.add_log(data.serialize())
        self.data.counters[current_client] = data.global_counter
        for game in data.games_dto:
            if self.has_to_be_inserted(game, current_client):
                inserted = False
                for i in range(len(self.list[current_client])):
                    if game.get(self.comparing_field) > self.data.list[current_client][i].get(self.comparing_field):
                        self.data.list[current_client].insert(i, game)
                        inserted = True
                        break
                if not inserted:
                    self.data.list[current_client].append(game)
                if len(self.data.list[current_client]) > self.top_size:
                    self.data.list[current_client].pop()
                self.data.min_time[current_client] = self.data.list[current_client][-1].get(self.comparing_field)

    def recover(self):
        checkpoint, must_reprocess = self.checkpoint.load_checkpoint()
        self.data.from_bytes(checkpoint)
        if must_reprocess:
            for log in self.logs.logs:
                data = DetectDTO(log).get_dto()
                self.process_data(data)
        else:
            self.logs.reset()
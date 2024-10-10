from system.commonsSystem.node.node import Node, PrematureEOFException
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_GENRE, STATE_Q2345
from system.commonsSystem.DTO.EOFDTO import EOFDTO, STATE_DEFAULT, STATE_OK
from system.commonsSystem.DTO.enums.OperationType import OperationType
import os
import logging
import sys

class Filter(Node):
    def __init__(self):
        super().__init__()
        self.genders = os.getenv("GENDERS").split(',')

    def is_gender(self, genders, wanted_gender):
        return wanted_gender in genders.split(',')
    
    def send_eof(self, data):
        client = data.get_client()
        for gender in self.genders:
            self.broker.public_message(sink=self.sink, message=EOFDTO(OperationType.OPERATION_TYPE_GAMES_EOF_DTO.value, client, STATE_DEFAULT, amount_sent=self.total_amount_sent[client][gender]).serialize(), routing_key=gender)
    
    def send_game(self, data:GamesDTO, gender):
        data.set_state(STATE_GENRE)
        self.broker.public_message(sink=self.sink, routing_key=gender, message=data.serialize())

    def update_amount_sent_by_node(self,client_id, gender, amount=0):
        if client_id not in self.amount_sent_by_node:
            self.amount_sent_by_node[client_id] = {}
        if gender not in self.amount_sent_by_node[client_id]:
            self.amount_sent_by_node[client_id][gender] = 0
        
        self.amount_sent_by_node[client_id][gender] += amount

    def process_data(self, data: GamesDTO):
        self.update_amount_received_by_node(data.get_client(), data.get_amount())
        for gender in self.genders:
            games_in_gender = []
            for game in data.games_dto:
                if self.is_gender(game.genres, gender):
                    games_in_gender.append(game) 
            if len(games_in_gender) > 0:
                self.send_game(GamesDTO(client_id=data.client_id, state_games=STATE_Q2345, games_dto=games_in_gender), gender)
            self.update_amount_sent_by_node(data.get_client(), gender, len(games_in_gender))
    
    def send_eof_confirmation(self, data: EOFDTO):
        client = data.get_client()
        amount_received_by_node = self.amount_received_by_node[client]
        for gender in self.genders:
            amount_sent_by_node = self.amount_sent_by_node[client][gender]
            logging.info(f"action: send_eof_confirmation | client: {client} | amount_received_by_node: {amount_received_by_node} | amount_sent_by_node {gender}: {amount_sent_by_node}")
            self.broker.public_message(sink=self.node_name + "_eofs", message=EOFDTO(data.operation_type, client,STATE_OK,gender,amount_received_by_node,amount_sent_by_node).serialize())

    def check_confirmations(self, data: EOFDTO):
        gender = data.get_attribute()
        logging.info(f"total amount sent en check confirmations: {self.total_amount_sent} data amount: {data.get_amount_sent()}")
        self.update_totals(data.client, gender, data.get_amount_received(), data.get_amount_sent())   
        logging.info(f"total amount sent:{self.total_amount_sent}")
        self.confirmations += 1
        logging.info(f"action: check_confirmations | client: {data.get_client()} | confirmations: {self.confirmations}")
        if self.confirmations == self.amount_of_nodes * len(self.genders) - 1:
            self.check_amounts(data)

    def check_amounts(self, data: EOFDTO):
        client = data.get_client()
        logging.info(f"action: check_amounts | client: {client} | total_amount_received: {self.total_amount_received[client]} | expected_total_amount_received: {self.expected_total_amount_received[client]}")
        if self.total_amount_received[client] == self.expected_total_amount_received[client]:
            self.pre_eof_actions(client)
            self.send_eof(data)
            self.clients.remove(client)
            self.clients_pending_confirmations.remove(client)
            self.confirmations = 0
            self.reset_amounts(data)
            if self.amount_of_nodes > 1:
                self.send_eof_finish(data)
            return
        if self.amount_of_nodes < 2:
            raise PrematureEOFException()
        self.reset_totals(client)
        for gender in self.genders:
            self.update_totals(client, gender, self.amount_received_by_node[client], self.amount_sent_by_node[client].get(gender, 0))
        self.ask_confirmations(data)

    def update_total_amount_sent(self,client, gender, amount=0):
        if client not in self.total_amount_sent:
            self.total_amount_sent[client] = {}
        if gender not in self.total_amount_sent[client]:
            self.total_amount_sent[client][gender] = 0
        
        self.total_amount_sent[client][gender] += amount

    def update_totals(self, client, gender, amount_received, amount_sent):
        if gender == self.genders[0]:
            self.update_total_amount_received(client, amount_received)
        self.update_total_amount_sent(client, gender, amount_sent)

    def inform_eof_to_nodes(self, data: EOFDTO):
        client = data.get_client()
        logging.info(f"action: inform_eof_to_nodes | client: {client}")
        self.reset_totals(client)
        for gender in self.genders:
            self.update_totals(client, gender, self.amount_received_by_node.get(client, 0), self.amount_sent_by_node[client].get(gender, 0))
        self.expected_total_amount_received[client] = data.get_amount_sent()
        self.clients_pending_confirmations.append(client)
        if self.amount_of_nodes < 2:
            self.check_amounts(data)
            return
        self.ask_confirmations(data)
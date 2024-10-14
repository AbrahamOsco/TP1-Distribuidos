from system.commonsSystem.DTO.EOFDTO import EOFDTO, STATE_DEFAULT, STATE_OK
from system.commonsSystem.node.routingPolicies.RoutingPolicy import RoutingPolicy
import logging

class EOFManagement:
    def __init__(self, routing: RoutingPolicy):
        self.amount_received_by_node = {}
        self.amount_sent_by_node = {}
        self.total_amount_received = {}
        self.total_amount_sent = {}
        self.expected_total_amount_received = {}
        self.routing = routing

    def update_amount_received_by_node(self,client_id, amount=0, tipo="default"):
        if client_id not in self.amount_received_by_node:
            self.amount_received_by_node[client_id] = {}
        if tipo not in self.amount_received_by_node[client_id]:
            self.amount_received_by_node[client_id][tipo] = 0
        
        self.amount_received_by_node[client_id][tipo] += amount
       
    def update_amount_sent_by_node(self,client_id, amount=0, tipo="default"):
        if client_id not in self.amount_sent_by_node:
            self.amount_sent_by_node[client_id] = {}
        if tipo not in self.amount_sent_by_node[client_id]:
            self.amount_sent_by_node[client_id][tipo] = 0
        
        self.amount_sent_by_node[client_id][tipo] += amount
   
    def update_total_amount_received(self,client_id, amount=0, tipo="default"):
        if client_id not in self.total_amount_received:
            self.total_amount_received[client_id] = {}
        if tipo not in self.total_amount_received[client_id]:
            self.total_amount_received[client_id][tipo] = 0
        
        self.total_amount_received[client_id][tipo] += amount
 
    def update_total_amount_sent(self,client_id, amount=0, tipo="default"):
        if client_id not in self.total_amount_sent:
            self.total_amount_sent[client_id] = {}
        if tipo not in self.total_amount_sent[client_id]:
            self.total_amount_sent[client_id][tipo] = 0
        
        self.total_amount_sent[client_id][tipo] += amount
    
    def get_total_amount_sent(self, client_id, tipo="default"):
        if client_id not in self.total_amount_sent:
            return 0
        if tipo not in self.total_amount_sent[client_id]:
            return 0
        return self.total_amount_sent[client_id][tipo]

    def get_total_amount_received(self, client_id, tipo="default"):
        if client_id not in self.total_amount_received:
            return 0
        if tipo not in self.total_amount_received[client_id]:
            return 0
        return self.total_amount_received[client_id][tipo]
    
    def get_amount_received_by_node(self, client_id, tipo="default"):
        if client_id not in self.amount_received_by_node:
            return 0
        if tipo not in self.amount_received_by_node[client_id]:
            return 0
        return self.amount_received_by_node[client_id][tipo]
    
    def get_amount_sent_by_node(self, client_id, tipo="default"):
        if client_id not in self.amount_sent_by_node:
            return 0
        if tipo not in self.amount_sent_by_node[client_id]:
            return 0
        return self.amount_sent_by_node[client_id][tipo]
    
    def set_expected_total_amount_received(self, client_id, routing_key, amount):
        if client_id not in self.expected_total_amount_received:
            self.expected_total_amount_received[client_id] = {}
        self.expected_total_amount_received[client_id][routing_key] = amount

    def get_expected_total_amount_received(self, client_id, routing_key):
        if client_id not in self.expected_total_amount_received:
            return 0
        if routing_key not in self.expected_total_amount_received[client_id]:
            return 0
        return self.expected_total_amount_received[client_id][routing_key]
    
    def get_eof_for_next_node(self, data: EOFDTO):
        client = data.get_client()
        sent_routing_keys = self.routing.get_routing_keys(data)
        eofs = []
        for routing_key in sent_routing_keys:
            message=EOFDTO(data.operation_type, client, STATE_DEFAULT,0,[("default", self.get_total_amount_sent(client, routing_key[0]))])
            eofs.append((message, routing_key[1]))
        return eofs

    def init_totals(self, client):
        self.reset_totals(client)
        self.total_amount_received[client] = self.amount_received_by_node[client].copy()
        self.total_amount_sent[client] = self.amount_sent_by_node[client].copy()

    def set_expected_total(self, client, data: EOFDTO):
        routing_key = self.routing.get_receive_routing_key(data)
        self.set_expected_total_amount_received(client, routing_key, data.get_amount_sent())

    def reset_totals(self, client):
        if client in self.total_amount_received:
            del self.total_amount_received[client]
        if client in self.total_amount_sent:
            del self.total_amount_sent[client]
    
    def reset_amounts(self,data: EOFDTO):
        client = data.get_client()
        if client in self.total_amount_received:
            del self.total_amount_received[client]
        if client in self.total_amount_sent:
            del self.total_amount_sent[client]
        if client in self.amount_received_by_node:
            del self.amount_received_by_node[client]
        if client in self.amount_sent_by_node:
            del self.amount_sent_by_node[client]

    def ready_to_send_eof(self, data: EOFDTO):
        routing_key = self.routing.get_receive_routing_key(data)
        client = data.get_client()
        total_amount_received = self.get_total_amount_received(client, routing_key)
        expected_total_amount_received = self.get_expected_total_amount_received(client, routing_key)
        logging.info(f"action: ready_to_send_eof | client: {client} | total_amount_received: {total_amount_received} | expected_total_amount_received: {expected_total_amount_received}")
        return total_amount_received == expected_total_amount_received
    
    def get_eof_confirmation(self, data: EOFDTO):
        client = data.get_client()
        receive_routing_key = self.routing.get_receive_routing_key(data)
        amount_received_by_node = self.get_amount_received_by_node(client, receive_routing_key)
        sent_routing_keys = self.routing.get_routing_keys(data)
        amount_sent_by_node = []
        for routing_key in sent_routing_keys:
            amount_sent_by_node.append((routing_key[0], self.get_amount_sent_by_node(client, routing_key[0])))
        return EOFDTO(data.operation_type,client,STATE_OK,amount_received_by_node,amount_sent_by_node)
    
    def update_totals(self, data: EOFDTO):
        client = data.get_client()
        receive_routing_key = self.routing.get_receive_routing_key(data)
        self.update_total_amount_received(client, data.amount_received, receive_routing_key)
        for sent in data.amount_sent:
            self.update_total_amount_sent(client, sent[1], sent[0])
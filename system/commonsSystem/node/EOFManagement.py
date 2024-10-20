from system.commonsSystem.DTO.EOFDTO import EOFDTO, STATE_DEFAULT, STATE_OK
from system.commonsSystem.node.routingPolicies.RoutingPolicy import RoutingPolicy
import logging

class EOFManagement:
    def __init__(self, routing: RoutingPolicy):
        self.routing = routing

    def get_eof_for_next_node(self, data: EOFDTO):
        client = data.get_client()
        sent_routing_keys = self.routing.get_routing_keys(data)
        eofs = []
        for routing_key in sent_routing_keys:
            message=EOFDTO(data.operation_type, client, STATE_DEFAULT, data.global_counter)
            eofs.append((message, routing_key[1]))
        return eofs

    def get_eof_confirmation(self, data: EOFDTO):
        client = data.get_client()
        ### ACA CHECKEAMOS CON PUL
        return EOFDTO(data.operation_type,client,STATE_OK)
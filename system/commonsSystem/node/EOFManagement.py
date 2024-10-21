from system.commonsSystem.DTO.EOFDTO import EOFDTO, STATE_DEFAULT, STATE_OK, STATE_CANCEL
from system.commonsSystem.node.routingPolicies.RoutingPolicy import RoutingPolicy

class EOFManagement:
    def __init__(self, routing: RoutingPolicy):
        self.routing = routing

    def get_eof_for_next_node(self, data: EOFDTO):
        client = data.get_client()
        sent_routing_keys = self.routing.get_routing_keys(data)
        eofs = []
        for routing_key in sent_routing_keys:
            message=EOFDTO(data.operation_type, client, STATE_DEFAULT, global_counter=data.global_counter)
            eofs.append((message, routing_key))
        return eofs

    def get_eof_confirmation(self, data: EOFDTO):
        client = data.get_client()
        return EOFDTO(data.operation_type,client,STATE_OK, global_counter=data.global_counter)
    
    def get_eof_cancel(self, data: EOFDTO):
        client = data.get_client()
        return EOFDTO(data.operation_type,client,STATE_CANCEL, global_counter=data.global_counter)
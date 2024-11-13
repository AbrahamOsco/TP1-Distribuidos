from system.commonsSystem.node.routingPolicies.RoutingPolicy import RoutingPolicy
from system.commonsSystem.DTO.EOFDTO import EOFDTO

class RoutingModulo(RoutingPolicy):
    def __init__(self, modulo):
        self.modulo = modulo

    def get_routing_keys(self, data: EOFDTO):
        return [str(data.global_counter % self.modulo)]
    
    def get_routing_key(self, data):
        return str(data.global_counter % self.modulo)
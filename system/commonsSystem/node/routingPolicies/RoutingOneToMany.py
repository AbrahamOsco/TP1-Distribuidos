from system.commonsSystem.node.routingPolicies.RoutingPolicy import RoutingPolicy
from system.commonsSystem.DTO.EOFDTO import EOFDTO

class RoutingOneToMany(RoutingPolicy):
    def __init__(self, destinations=[]):
        self.destinations = [(destination, destination) for destination in destinations]

    def get_routing_keys(self, data: EOFDTO):
        return self.destinations
    
    def get_receive_routing_key(self, data: EOFDTO):
        return "default"
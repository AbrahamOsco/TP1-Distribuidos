from system.commonsSystem.node.routingPolicies.RoutingPolicy import RoutingPolicy
from system.commonsSystem.DTO.EOFDTO import EOFDTO

class RoutingOneToOne(RoutingPolicy):
    def __init__(self):
        pass

    def get_routing_keys(self, data: EOFDTO):
        return [data.get_type()]
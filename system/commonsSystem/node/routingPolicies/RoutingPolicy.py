from system.commonsSystem.DTO.EOFDTO import EOFDTO

class RoutingPolicy():
    def get_routing_keys(self, data: EOFDTO):
        return []
    
    def get_receive_routing_key(self, data: EOFDTO):
        return ""
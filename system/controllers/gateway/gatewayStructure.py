from system.commonsSystem.node.structures.structure import Structure
from multiprocessing import Array
from system.controllers.gateway.GlobalCounter import GlobalCounter

class GatewayStructure(Structure):
    def __init__(self, max_clients):
        self.clients_allow = Array('b', [True] * max_clients)

    def reset(self, client_id):
        pass

    def to_bytes(self):
        structure_bytes = bytearray()
        structure_bytes.extend(GlobalCounter.get_current().to_bytes(6, byteorder='big'))
        return bytes(structure_bytes)
    
    def from_bytes(self, data):
        offset = 0
        global_counter = int.from_bytes(data[offset:offset+6], byteorder='big')
        offset += 6
        GlobalCounter.set_current(global_counter)
        return self, offset
    
    def print_state(self):
        pass
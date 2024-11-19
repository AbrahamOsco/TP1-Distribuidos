from system.commonsSystem.node.structures.structure import Structure
import logging
from multiprocessing import Array

class GatewayStructure(Structure):
    def __init__(self, max_clients):
        self.clients_allow = Array('b', [True] * max_clients)

    def reset(self, client_id):
        pass

    def to_bytes(self):
        structure_bytes = bytearray()
        return bytes(structure_bytes)
    
    def from_bytes(self, data):
        offset = 0
        return self, offset
    
    def print_state(self):
        pass
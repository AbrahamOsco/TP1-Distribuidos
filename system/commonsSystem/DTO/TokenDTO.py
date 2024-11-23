from enum import Enum

class TypeToken(Enum):
    ELECTION = 0
    COORDINATOR = 1
    ACK = 2
    DUMMY = 3

class TokenDTO:
    def __init__(self, a_type: TypeToken, dic_medics ={}, leader_id =0, numeric_ip_leader=""):
        self.a_type = a_type
        self.dic_medics = dic_medics # {medic_id: medic_numeric_ip}
        self.leader_id = leader_id
        self.numeric_ip_leader = numeric_ip_leader

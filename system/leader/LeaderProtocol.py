import logging
from common.protocol.Protocol import Protocol
from system.commonsSystem.DTO.TokenDTO import TokenDTO, TypeToken
import time
time_to_sleep = 0

class LeaderProtocol(Protocol):

    def __init__(self, socket):
        super().__init__(socket)

    def send_tokenDTO(self, a_tokenDTO:TokenDTO):
        time.sleep(time_to_sleep)
        if not isinstance(a_tokenDTO, TokenDTO):
            raise ValueError("Expected a TokenDTO instance")
        self.send_number_n_bytes(1, a_tokenDTO.a_type.value)
        self.send_number_n_bytes(1, len(a_tokenDTO.dic_medics))
        for medic_id, medic_ip in a_tokenDTO.dic_medics.items():
            self.send_number_n_bytes(2, medic_id)
            self.send_string(medic_ip)
        self.send_number_n_bytes(2, a_tokenDTO.leader_id)
        self.send_string(a_tokenDTO.numeric_ip_leader)

    def recv_tokenDTO(self, ) -> TokenDTO:
        a_type = self.recv_number_n_bytes(1)
        dic_medics = {}
        amount = self.recv_number_n_bytes(1)
        for _ in range(amount):
            medic_id = self.recv_number_n_bytes(2)
            medic_ip = self.recv_string()
            dic_medics[medic_id] = medic_ip
        leader_id = self.recv_number_n_bytes(2)
        numeric_ip_leader = self.recv_string()
        try:
            type_token = TypeToken(a_type)
        except ValueError:
            raise ValueError(f"Invalid token type received: {a_type}")

        a_tokenDTO = TokenDTO(type_token, dic_medics, leader_id, numeric_ip_leader)
        return a_tokenDTO


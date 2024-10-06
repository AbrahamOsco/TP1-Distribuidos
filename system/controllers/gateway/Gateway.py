from common.socket.Socket import Socket
from system.commonsSystem.node.node import Node
import logging
import multiprocessing
from system.commonsSystem.protocol.ServerProtocol import ServerProtocol
from system.commonsSystem.DTO.GamesDTO import GamesDTO

class Gateway(Node):
    def __init__(self):
        self.socket_accepter = Socket(port=12345)
        self.current_client = 0
        self.processes = []
        super().__init__()

    def accept_a_connection(self):
        logging.info("action: Waiting a client to connect | result: pending ⌚")
        self.socket_peer, addr = self.socket_accepter.accept()
        logging.info("action: Waiting a client to connect | result: success ✅")
        self.protocol = ServerProtocol(self.socket_peer)
    
    def start(self):
        self.processes.append(multiprocessing.Process(target=self.run))
        while True:
            self.accept_a_connection()
            while True:
                raw_dto = self.protocol.recv_data_raw()
                self.broker.public_message(sink=self.sink, message = raw_dto.serialize(), routing_key="default")

    def process_data(self, data: GamesDTO):
        result = data.to_result()
        self.protocol.send_result(result)

    def abort(self):
        self.stop()
        for process in self.processes:
            process.terminate()
            process.join()
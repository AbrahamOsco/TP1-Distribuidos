from common.socket.Socket import Socket
from system.ServerProtocol import ServerProtocol
import logging

class Input:
    def __init__(self):
        self.initialize_log()
        self.socket_accepter = Socket(port =12345)
        logging.info("action: Waiting a client to connect result: pending ⌚")
        self.socket_peer, addr = self.socket_accepter.accept()
        logging.info("action: Waiting a client to connect result: success ✅")
        self.protocol = ServerProtocol(self.socket_peer)
    
    def run(self):
        logging.info("action: Input prepare to recv data! | 😶‍🌫️🍄")
        while True:
            id_client, operation_type, list_items = self.protocol.recv_data_raw()
            logging.info("action: The data batches received | result: success | 🍄")
            logging.info(f"client_id: {id_client} operation: {operation_type} | list_items: {list_items}")
    
    def initialize_log(self, logging_level= logging.INFO):
        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging_level,
            datefmt='%Y-%m-%d %H:%M:%S',
        )
    # funcion para filtrar y luego codear un exchange con routing key= game q pushee a las queues games_q1 y games_q2345
    # y luego un mensaje con ruting_key=review q pushe a la queue reviwes_raw

    def filter_data(self):
        pass
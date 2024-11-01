from system.commonsSystem.utils.log import initialize_config_log 
from common.socket.Socket import Socket
import threading
import os
import logging


class LeaderElection:
    def __init__(self):
        self.id = os.getenv("NODE_ID")
        self.ring_size = os.getenv("RING_SIZE")
        self.config_params = initialize_config_log()
        self.myHostname = "node"+str(self.id) 
        self.sktAceptador = Socket(port =10 + int(self.id)) # puerto 10100 para el nodo 100

    def accepteConnecton(self):
        while True:
            skt_peer, addr = self.sktAceptador.accept()
            if skt_peer is not None:
                logging.info(f"action: accept | result: success ✅ | addr: {addr}")
                threading.Thread(target=self.handle_connection, args=(skt_peer, addr)).start()
            else:
                logging.error(f"action: accept | result: fail ❌ | error: {addr}")

    def run(self):
        logging.info(f"Leader election started 💯: {self.ring_size}")
        threading.Thread(target=self.accepteConnecton).start()
        



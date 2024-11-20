from system.commonsSystem.heartbeatClient.HeartbeatClient import HeartbeatClient
from system.commonsSystem.utils.connectionLeader import PART_INITIAL_PORT_GLOBAL, get_host_name, get_service_name
import time
import logging
import os
import signal

class GenericNodeToy:
    def __init__(self):
        self.my_id = int(os.getenv("NODE_ID"))
        self.hearbeatClient = HeartbeatClient(self.my_id)
        self.hearbeatClient.run()
        signal.signal(signal.SIGTERM, self.sign_term_handler)
        self.nodes = []
    
    def run(self):
        logging.info("hii!")
    
    def sign_term_handler(self, signum, frame):
        logging.info(f"[{self.id}] ⚡ {signum} SIGTERM Bye! 💯 💯 🅰️")
        self.hearbeatClient.free_resources()

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',)
    logging.info("🥍 Alive")
    node = GenericNodeToy()
    node.run()

main()
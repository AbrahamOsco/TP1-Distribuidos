from system.leader.HeartbeatClient import HeartbeatClient
from system.commonsSystem.utils.connectionLeader import PART_INITIAL_PORT_GLOBAL, get_host_name, get_service_name
import time
import logging
import os
import signal

class GenericNodeToy:
    def __init__(self):
        self.my_id = os.getenv("NODE_ID")
        self.my_hostname = get_host_name(self.my_id)
        self.my_service_name = get_service_name(self.my_id)
        self.id = os.getenv("NODE_ID")
        self.hearbeatClient = HeartbeatClient(self.my_hostname, self.my_service_name)
        self.hearbeatClient.run()
        signal.signal(signal.SIGTERM, self.sign_term_handler)

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
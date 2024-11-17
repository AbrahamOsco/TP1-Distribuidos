from system.leader.HeartbeatClient import HeartbeatClient
from system.commonsSystem.utils.connectionLeader import PART_INITIAL_PORT_GLOBAL, get_host_name, get_service_name
import time
import logging
import os

def main():
    my_id = os.getenv("NODE_ID")
    my_hostname = get_host_name(my_id)
    my_service_name = get_service_name(my_id)
    #hearbeatClient = HeartbeatClient(my_hostname, my_service_name)
    #hearbeatClient.run()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')
    while True:
        logging.info("LOGGIN For testing nothign to do 🗡️ 🅰️ 🅱️ 🥳 ")
        logging.info(f"INFO: id:{my_id} hostName: {my_hostname} my_service: {my_service_name} ")
        time.sleep(3)

main()
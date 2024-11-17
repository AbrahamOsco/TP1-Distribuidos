from system.leader.HeartbeatClient import HeartbeatClient
from system.commonsSystem.utils.connectionLeader import PART_INITIAL_PORT_GLOBAL, get_host_name, get_service_name
import time
import logging
import os

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',)
    logging.info("🅰️🅰️🅰️🅰️🅰️ 🥍[ALIVE]🥍🥍🥍🥍🥍🥍🥍🥍🥍🥍🥍🥍🥍")
    my_id = os.getenv("NODE_ID")
    my_hostname = get_host_name(my_id)
    my_service_name = get_service_name(my_id)
    hearbeatClient = HeartbeatClient(my_hostname, my_service_name)
    hearbeatClient.run()
    while True:
        time.sleep(3)

main()
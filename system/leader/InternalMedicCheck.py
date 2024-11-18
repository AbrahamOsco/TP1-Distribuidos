from system.commonsSystem.utils.connectionLeader import get_host_name, get_service_name
from system.leader.common_leader import OFFSET_MEDIC_SERVER_INTERN
import logging
import traceback
import time
import socket
import logging
import threading

VERBOSE = 1
TIME_OUT_HEALTH_CHECK = 0.5
FAIL = 0
SUCCESS = 1
PING_ATTEMPTS = 1

class InternalMedicCheck:
    hostname = None
    service_name = None
    socket = None


    @classmethod
    def try_to_connect_with_medic(cls, my_id, verbose) -> bool:
        cls.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cls.socket.settimeout(TIME_OUT_HEALTH_CHECK)
        message = "ping".encode('utf-8')
        i = 0
        try:
            while i < PING_ATTEMPTS:
                cls.socket.sendto(message, (cls.hostname, cls.service_name))
                i += 1
            data, addr = cls.socket.recvfrom(1024)
            if data == b'ping'and verbose == VERBOSE:
                logging.info(f"[{my_id}] Node: {cls.hostname} is Alive! ✅")
            cls.socket.close()
            return True
        except socket.timeout:
            cls.socket.close()
            logging.info(f"[{my_id}] This Node [{cls.hostname}] is 💀 Timeout!")
            logging.info(f"[{my_id}] End join load a lot?? 🪓 ")
            return False
        except socket.gaierror as e:
            cls.socket.close()
            logging.error(f"[{my_id}] -> Node: [{cls.hostname}] is falling Error: {e}  👈")
            return False
        except Exception as e:
            cls.socket.close()
            traceback.print_exc()
            logging.info(f"[{cls.hostname}] Other type of Error in healtcheck {e} 👈")
            return False
        return False
    
    @classmethod
    def is_alive(cls, my_id, node_id_to_check, verbose = VERBOSE) -> bool:
        if my_id == node_id_to_check:
            return True
        cls.hostname = get_host_name(node_id_to_check)
        cls.service_name = get_service_name(node_id_to_check + OFFSET_MEDIC_SERVER_INTERN)
        return cls.try_to_connect_with_medic(my_id, verbose)

    @classmethod
    def try_to_get_leader_id(cls, my_id, node_id_to_check, verbose = VERBOSE) -> int or None:
        cls.hostname = get_host_name(node_id_to_check)
        cls.service_name = get_service_name(node_id_to_check + OFFSET_MEDIC_SERVER_INTERN)
        if cls.try_to_connect_with_medic(my_id, VERBOSE):
            cls.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = "leader_id".encode('utf-8')
            cls.socket.sendto(message, (cls.hostname, cls.service_name))
            data, addr = cls.socket.recvfrom(1024)
            if data != b"no_leader":
                if cls.is_alive(my_id, int(data)):
                    cls.socket.close()
                    return int(data)
            cls.socket.close()
        return None

from system.commonsSystem.utils.connectionLeader import get_host_name, get_service_name
from system.leader.common_leader import OFFSET_MEDIC_PORT_SERVER_INTERN
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
    leader_id_dead = None

    @classmethod
    def set_leader_id_dead(cls, leader_id_dead):
        cls.leader_id_dead = leader_id_dead

    @classmethod
    def is_alive_with_ip(cls,my_id, node_id_to_check, ip_numeric, verbose = VERBOSE) -> bool:
        cls.hostname = ip_numeric
        cls.service_name = get_service_name(node_id_to_check + OFFSET_MEDIC_PORT_SERVER_INTERN)
        return cls.try_to_connect_with_medic(my_id, verbose)

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
            logging.info(f"[{my_id}] This Node with this port: [{cls.service_name}] Timeout!")
            return False
        except socket.gaierror as e:
            cls.socket.close()
            logging.error(f"[{my_id}] -> Node: [{cls.hostname}] Can't connect (Resolve DNS): {e} 👈")
            return False
        except Exception as e:
            cls.socket.close()
            traceback.print_exc()
            logging.info(f"[{cls.hostname}] Other type of Error in healtcheck {e} 👈")
            return False
        cls.socket.close()
        return False
    
    @classmethod
    def clean_leader_id(cls):
        cls.leader_id_dead = None

    @classmethod
    def get_ip_numeric(cls, a_id):
        cls.hostname = get_host_name(a_id)
        cls.service_name = get_service_name(a_id + OFFSET_MEDIC_PORT_SERVER_INTERN)
        cls.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cls.socket.sendto(b"ping", (cls.hostname, cls.service_name))
        data, addr = cls.socket.recvfrom(1024)
        return addr[0]

    @classmethod
    def is_alive(cls, my_id, node_id_to_check, verbose = VERBOSE) -> bool:
        if cls.leader_id_dead and node_id_to_check == cls.leader_id_dead:
            return False
        if my_id == node_id_to_check:
            return True
        cls.hostname = get_host_name(node_id_to_check)
        cls.service_name = get_service_name(node_id_to_check + OFFSET_MEDIC_PORT_SERVER_INTERN)
        return cls.try_to_connect_with_medic(my_id, verbose)

    @classmethod
    def try_get_leader_data(cls, my_id, node_id_to_check, verbose = VERBOSE) -> int or None:
        if node_id_to_check == cls.leader_id_dead:
            return None
        cls.hostname = get_host_name(node_id_to_check)
        cls.service_name = get_service_name(node_id_to_check + OFFSET_MEDIC_PORT_SERVER_INTERN)
        if cls.try_to_connect_with_medic(my_id, VERBOSE):
            cls.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = "leader_id".encode('utf-8')
            cls.socket.sendto(message, (cls.hostname, cls.service_name))
            data, addr = cls.socket.recvfrom(1024)
            if data != b"no_leader":
                data = data.decode('utf-8').split("|")
                if cls.is_alive_with_ip(my_id, int(data[0]), data[1]):
                    cls.socket.close()
                    return (int(data[0]), data[1])
            cls.socket.close()
        return None

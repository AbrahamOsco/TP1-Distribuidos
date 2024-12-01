from enum import Enum

class NodeStatus(Enum):
    ACTIVE = 0
    DEAD = 1
    RECENTLY_REVIVED = 2


class NodeInfo:
    def __init__(self, hostname: str, service_name: int):
        self.hostname = hostname
        self.numeric_ip = None
        self.service_name = service_name
        self.last_time = None
        self.status = NodeStatus.ACTIVE
        self.active = True
        self.counter_loading = 0

    def update_lastime(self, time_received):
        self.last_time = time_received
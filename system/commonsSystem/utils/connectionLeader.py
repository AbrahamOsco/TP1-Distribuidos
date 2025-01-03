import os
PART_INITIAL_PORT_GLOBAL = "20"
OFFSET_MEDIC_HOSTNAME = 500


def get_host_name(a_id: str):
    a_id = int(a_id)
    node_name = os.getenv("NODE_INSTANCE_NAME") #medic_0
    if a_id >= OFFSET_MEDIC_HOSTNAME:
        number_linked_node = OFFSET_MEDIC_HOSTNAME #using sockets we can obtain medic ip.
        return f"{node_name[:-1]}{a_id-number_linked_node}"
    return f"{node_name}"

def get_service_name(a_id: int):
    a_id = int(a_id)
    return int(f"{PART_INITIAL_PORT_GLOBAL}{a_id}")

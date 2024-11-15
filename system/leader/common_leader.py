NAME_OF_NODO_MEDIC = "medic"
OFF_SET_INTERNAL_MEDICS = 100

def get_service_name(id: int):
    return int(f"20{id}")

def get_host_name_medic(id: int):
    return f"{NAME_OF_NODO_MEDIC}{id-100}"

def ids_to_msg(message: str, ids: list[int]):
    return message + "|" + "|".join([str(x) for x in ids])


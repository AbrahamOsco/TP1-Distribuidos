
OFFSET_MEDIC_SERVER_INTERN = 100
def ids_to_msg(message: str, ids: list[int]):
    return message + "|" + "|".join([str(x) for x in ids])


from EOFDTO import EOFDTO
from GameDTO import GameDTO

def getDTO(data):
    if "EOF" in data:
        return EOFDTO.from_string(data)
    elif "GAME" in data:
        return GameDTO.from_string(data)
    else:
        return None
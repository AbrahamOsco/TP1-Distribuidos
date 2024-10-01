from system.commonsSystem.DTO.EOFDTO import EOFDTO
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.DTO.ReviewDTO import ReviewDTO

def getDTO(data):
    if "EOF" in data:
        return EOFDTO.from_string(data)
    elif "GAME" in data:
        return GameDTO.from_string(data)
    elif "REVIEW" in data:
        return ReviewDTO.from_string(data)
    else:
        return None
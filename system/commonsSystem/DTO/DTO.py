from EOFDTO import EOFDTO

def getDTO(data):
    if "EOF" in data:
        return EOFDTO.from_string(data)
    else:
        return None
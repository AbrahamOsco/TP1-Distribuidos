import logging
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.GameDTO import GameDTO
OPERATION_TYPE_STR = 27

class BrokerSerializer:
    def __init__(self):
        self.command_serialize = {'str': self.serialize_str}
        self.command_deserialize = {'str': self.deserialize_str}
        pass

    def serialize(self, message):
        logging.info(f" Serialize: 🍎 type(message):{type(message)}, type(message).__name__: {type(message).__name__}")
        type_message = type(message).__name__
        return self.command_serialize[type_message](message)
        
        if isinstance(message, GamesDTO):
            return self.serialize_GamesDTO(message)

    def deserialize(self, message):
        logging.info(f" Deserialize 🍍 type(message):{type(message)}, type(message).__name__: {type(message).__name__}")
        offset = 0
        #Leemos el primer byte para saber que entidad es y luego de eso obtenemos el resultado podemos 
        # leer nuevamente el 1er byte, cosa q en los sockets no se podia.
        operation_type = int.from_bytes(message[offset:offset+1], byteorder='big')
        
        if operation_type == OPERATION_TYPE_STR:
            result, offset = self.deserialize_str(message, 0)
            return result

    def serialize_GamesDTO(self, gamesDTO: GamesDTO):
        games_bytes = bytearray()
        games_bytes.extend(gamesDTO.operation_type.to_bytes(1, byteorder='big'))
        games_bytes.extend(gamesDTO.client_id.to_bytes(1, byteorder='big'))
        games_bytes.extend(gamesDTO.state_games.to_bytes(1, byteorder='big'))
        games_bytes.extend(len(gamesDTO.games_dto).to_bytes(2, byteorder='big'))

        for game in gamesDTO.games_dto:
            games_bytes.extend(self.serialize_GameDTO(game, gamesDTO.state_games))

        return bytes(games_bytes)
    
    def serialize_GameDTO(self, gameDTO: GameDTO, state_games:int):
        game_bytes = bytearray()
        game_bytes.extend(gameDTO.operation_type.to_bytes(1, byteorder='big'))
        game_bytes.extend(gameDTO.client_id.to_bytes(1, byteorder='big')) # ver si esto sirve sino lo sacamos de gameDTO lo mando igual

        # aca preguntar segun el state games enviar q atributos y que no. 
        game_bytes.extend(self.serialize_str(gameDTO.app_id))
        game_bytes.extend(self.serialize_str(gameDTO.name))
        game_bytes.extend(self.serialize_str(gameDTO.release_date))

        game_bytes.extend(gameDTO.windows.to_bytes(1, byteorder='big'))
        game_bytes.extend(gameDTO.mac.to_bytes(1, byteorder='big'))
        game_bytes.extend(gameDTO.linux.to_bytes(1, byteorder='big'))

        game_bytes.extend(self.serialize_str(gameDTO.avg_playtime_forever))
        game_bytes.extend(self.serialize_str(gameDTO.genres))

        return game_bytes

    def serialize_str(self, a_string:str):
        logging.info("action: serialize string 🍰 | status: pending ⌚")
        string_in_bytes = a_string.encode('utf-8')
        # Enviar un String es el ti po de operacion OPERATION_TYPE_STR
        serialized_string = OPERATION_TYPE_STR.to_bytes(1, byteorder='big') 
        serialized_string += len(string_in_bytes).to_bytes(2, byteorder='big')
        serialized_string += string_in_bytes
        logging.info("action: serialize string 🍰 | status: success ✅")
        
        return serialized_string

    def deserialize_str(self, data, offset):
        offset = 0 
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset +=1

        string_length = int.from_bytes(data[offset:offset+2], byteorder='big')
        offset += 2
        string = data[offset:offset + string_length].decode('utf-8')
        offset += string_length
        return string, offset


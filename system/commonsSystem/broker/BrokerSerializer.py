import logging
from system.commonsSystem.DTO.DecadeDTO import DecadeDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_GAMES_INITIAL, STATE_PLATFORM
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.DTO.GenreDTO import GenreDTO
from system.commonsSystem.DTO.PlatformDTO import PlatformDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.GamesIndexDTO import GamesIndexDTO
from system.commonsSystem.DTO.ReviewsIndexDTO import ReviewsIndexDTO


OPERATION_TYPE_STR = 27

class BrokerSerializer:
    def __init__(self):
        self.command_serialize = {
            'str': self.serialize_str,
            'GamesDTO': self.serialize_GamesDTO,
            'PlatformDTO': self.serialize_PlatformDTO,
            'GenreDTO': self.serialize_GenreDTO,
            'DecadeDTO': self.serialize_DecadeDTO,
            'GamesIndexDTO':self.serialize_a_IndexDTO,
            'ReviewsIndexDTO':self.serialize_a_IndexDTO,
        }

        self.command_deserialize = {
            OperationType.OPERATION_TYPE_STR: self.deserialize_str,
            OperationType.OPERATION_TYPE_GAME: self.deserialize_gameDTO,
            OperationType.OPERATION_TYPE_GAMES_DTO: self.deserialize_gamesDTO,
            OperationType.OPERATION_TYPE_PLATFORM_DTO: self.deserialize_platformDTO,
            OperationType.OPERATION_TYPE_GENRE_DTO: self.deserialize_genreDTO,
            OperationType.OPERATION_TYPE_DECADE_DTO: self.deserialize_decadeDTO,
            OperationType.OPERATION_TYPE_GAMES_INDEX_DTO: self.deserialize_a_IndexDTO,
            OperationType.OPERATION_TYPE_REVIEWS_INDEX_DTO: self.deserialize_a_IndexDTO
        }

    def serialize(self, message):
        type_message = type(message).__name__
        return self.command_serialize[type_message](message)

    def deserialize(self, message):
        offset = 0
        #Primer byte indica el tipo de operacion, usando Command, obtenemos la funcion a usar. 
        operation_type = int.from_bytes(message[offset:offset+1], byteorder='big')

        try:
            result, offset = self.command_deserialize[OperationType(operation_type)](message, 0)
        except KeyError:
            logging.error(f"Unknown operation type: {operation_type}")

        return result

    def serialize_DecadeDTO(self, decadeDTO: DecadeDTO):
        decade_bytes = bytearray()
        decade_bytes.extend(decadeDTO.operation_type.value.to_bytes(1, byteorder='big'))
        decade_bytes.extend(decadeDTO.client_id.to_bytes(1, byteorder='big'))
        decade_bytes.extend(self.serialize_str(decadeDTO.name))
        decade_bytes.extend(decadeDTO.year.to_bytes(4, byteorder='big'))
        decade_bytes.extend(decadeDTO.average_playtime.to_bytes(4, byteorder='big'))
        return bytes(decade_bytes)

    def serialize_GenreDTO(self, genreDTO: GenreDTO):
        genre_bytes = bytearray()
        genre_bytes.extend(genreDTO.operation_type.value.to_bytes(1, byteorder='big'))
        genre_bytes.extend(genreDTO.client_id.to_bytes(1, byteorder='big'))
        genre_bytes.extend(self.serialize_str(genreDTO.name))
        genre_bytes.extend(self.serialize_str(genreDTO.gender))
        genre_bytes.extend(genreDTO.year.to_bytes(4, byteorder='big'))
        genre_bytes.extend(genreDTO.average_playtime.to_bytes(4, byteorder='big'))
        return bytes(genre_bytes)


    def serialize_a_IndexDTO(self, aIndexDTO):
        index_bytes = bytearray()
        index_bytes.extend(aIndexDTO.operation_type.value.to_bytes(1, byteorder='big'))
        index_bytes.extend(aIndexDTO.client_id.to_bytes(1, byteorder='big'))
        
        index_bytes.extend(len(aIndexDTO.data_raw).to_bytes(2, byteorder='big'))
        for element in aIndexDTO.data_raw:
            index_bytes.extend(len(element).to_bytes(2, byteorder='big'))
            for field in element:
                index_bytes.extend(self.serialize_str(field))

        index_bytes.extend(len(aIndexDTO.indexes).to_bytes(1, byteorder='big'))
        for name, index in aIndexDTO.indexes.items():
            index_bytes.extend(self.serialize_str(name))
            index_bytes.extend(index.to_bytes(1, byteorder='big'))
        return bytes(index_bytes)

    def deserialize_a_IndexDTO(self, data, offset):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1

        items_raw_length = int.from_bytes(data[offset:offset+2], byteorder='big')
        offset += 2
        items_raw = []
        for i in range(items_raw_length):
            a_item_length = int.from_bytes(data[offset:offset+2], byteorder='big')
            offset += 2
            a_item = []
            for j in range(a_item_length):
                field, offset = self.deserialize_str(data, offset)
                a_item.append(field)
            items_raw.append(a_item)

        indexes_length = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        indexes = {}
        for i in range(indexes_length):
            name, offset = self.deserialize_str(data, offset)
            index = int.from_bytes(data[offset:offset+1], byteorder='big')
            offset += 1
            indexes[name] = index
        if operation_type == OperationType.OPERATION_TYPE_GAMES_INDEX_DTO:
            return GamesIndexDTO(client_id=client_id, indexes=indexes, games_raw= items_raw), offset
        return ReviewsIndexDTO(client_id=client_id, indexes=indexes, reviews_raw= items_raw), offset

    def serialize_PlatformDTO(self, platformDTO: PlatformDTO):
        platform_bytes = bytearray()
        platform_bytes.extend(platformDTO.operation_type.value.to_bytes(1, byteorder='big'))
        platform_bytes.extend(platformDTO.client_id.to_bytes(1, byteorder='big'))
        platform_bytes.extend(platformDTO.windows.to_bytes(4, byteorder='big'))
        platform_bytes.extend(platformDTO.mac.to_bytes(4, byteorder='big'))
        platform_bytes.extend(platformDTO.linux.to_bytes(4, byteorder='big'))
        return bytes(platform_bytes)

    def serialize_GamesDTO(self, gamesDTO: GamesDTO):
        games_bytes = bytearray()
        games_bytes.extend(gamesDTO.operation_type.value.to_bytes(1, byteorder='big'))
        games_bytes.extend(gamesDTO.client_id.to_bytes(1, byteorder='big'))
        games_bytes.extend(gamesDTO.state_games.to_bytes(1, byteorder='big'))
        games_bytes.extend(len(gamesDTO.games_dto).to_bytes(2, byteorder='big'))

        for game in gamesDTO.games_dto:
            games_bytes.extend(self.serialize_GameDTO(game, gamesDTO.state_games))

        return bytes(games_bytes)
    
    def serialize_GameDTO(self, gameDTO: GameDTO, state_games:int):
        game_bytes = bytearray()
        game_bytes.extend(gameDTO.operation_type.value.to_bytes(1, byteorder='big'))
        # Preguntar segun el state games enviar q atributos y que no. 
        if state_games == STATE_PLATFORM:
            game_bytes.extend(gameDTO.windows.to_bytes(1, byteorder='big'))
            game_bytes.extend(gameDTO.mac.to_bytes(1, byteorder='big'))
            game_bytes.extend(gameDTO.linux.to_bytes(1, byteorder='big'))
            return game_bytes
        
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
        serialized_string = bytearray()
        string_in_bytes = a_string.encode('utf-8')
        serialized_string.extend(OperationType.OPERATION_TYPE_STR.value.to_bytes(1, byteorder='big'))
        serialized_string.extend(len(string_in_bytes).to_bytes(2, byteorder='big'))
        serialized_string.extend(string_in_bytes)
        return serialized_string

    def deserialize_str(self, data, offset):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        string_length = int.from_bytes(data[offset:offset+2], byteorder='big')
        offset += 2
        string = data[offset:offset + string_length].decode('utf-8')
        offset += string_length
        return string, offset

    def deserialize_decadeDTO(self, data, offset):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        name, offset = self.deserialize_str(data, offset)
        year = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        average_playtime = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        return DecadeDTO(client_id=client_id, name=name, year=year, average_playtime=average_playtime), offset

    def deserialize_genreDTO(self, data, offset):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        name, offset = self.deserialize_str(data, offset)
        gender, offset = self.deserialize_str(data, offset)
        year = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        average_playtime = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        return GenreDTO(client_id=client_id, name=name, gender=gender, year=year, average_playtime=average_playtime), offset

    def deserialize_platformDTO(self, data, offset):
        client_id = int.from_bytes(data[offset:offset + 1], byteorder='big')
        offset += 1
        windows = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        mac = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        linux = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        return PlatformDTO(client_id=client_id, windows=windows, mac=mac, linux=linux), offset

    def deserialize_gamesDTO(self, data, offset):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        state_games = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        games_dto_length = int.from_bytes(data[offset:offset+2], byteorder='big')
        offset += 2
        
        some_games_dto = []
        for i in range(games_dto_length):
            game, offset = self.deserialize_gameDTO(data, offset, state_games) #asigna a offset el nuevo valor de offset y se lo guarda pal prox loop.
            some_games_dto.append(game)
        gamesDTO = GamesDTO(state_games =state_games, client_id =client_id, games_dto =some_games_dto)
        return gamesDTO, offset
    
    #con el state_games vemos q atributos tenemos unicamente en cuenta.
    def deserialize_gameDTO(self, data, offset, state_games:int):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        if state_games == STATE_PLATFORM:
            windows = int.from_bytes(data[offset:offset+1], byteorder='big')
            offset += 1
            mac = int.from_bytes(data[offset:offset+1], byteorder='big')
            offset += 1
            linux = int.from_bytes(data[offset:offset+1], byteorder='big')
            offset += 1
            return GameDTO(windows =windows, mac =mac, linux =linux), offset
        
        app_id, offset = self.deserialize_str(data, offset)
        name, offset = self.deserialize_str(data, offset)
        release_date, offset = self.deserialize_str(data, offset)
        windows = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        mac = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        linux = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        avg_playtime_forever, offset = self.deserialize_str(data, offset)
        genres, offset = self.deserialize_str(data, offset)
        return GameDTO(app_id =app_id, name =name, windows =windows,
                       mac =mac, linux =linux, genres =genres, release_date =release_date, 
                       avg_playtime_forever =avg_playtime_forever), offset

import logging
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.enums.StateGame import StateGame
from system.commonsSystem.DTO.SerializerGame.SerializerInitial import SerializerInitial
from system.commonsSystem.DTO.SerializerGame.SerializerPlatform import SerializerPlatform
from system.commonsSystem.DTO.SerializerGame.SerializeGender import SerializerGender
from system.commonsSystem.DTO.SerializerGame.SerializerIDName import SerializerIDName
from system.commonsSystem.DTO.SerializerGame.SerializerQ2345 import SerializerQ2345
from system.commonsSystem.DTO.SerializerGame.SerializerDecade import SerializerDecade

class GameDTO:
    def __init__(self, app_id =0, name ="", windows =0,
            mac =0, linux =0, genres ="", release_date ="", avg_playtime_forever =0):
        self.operation_type = OperationType.OPERATION_TYPE_GAME
        self.app_id = app_id
        self.name = name
        self.release_date = release_date
        self.windows = int(windows)
        self.mac = int(mac)
        self.linux = int(linux)
        self.avg_playtime_forever = avg_playtime_forever
        self.genres = genres
        self.command_serialize = {
            StateGame.STATE_GAMES_INITIAL.value: SerializerInitial(), 
            StateGame.STATE_PLATFORM.value: SerializerPlatform(),
            StateGame.STATE_GENDER.value: SerializerGender(),
            StateGame.STATE_Q2345.value: SerializerQ2345(),
            StateGame.STATE_DECADE.value: SerializerDecade(),
            StateGame.STATE_ID_NAME.value: SerializerIDName(),
        }

    def serialize(self, state_games:int):
        return self.command_serialize[state_games].serialize(self)

    def deserialize(self, data, offset, state_games:int):
        return self.command_serialize[state_games].deserialize(data, offset)


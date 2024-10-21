import os
from system.commonsSystem.node.grouperNode import GrouperNode
from system.commonsSystem.DTO.GamesDTO import STATE_PLAYTIME

class Grouper(GrouperNode):
    def __init__(self):
        super().__init__(STATE_PLAYTIME, 2, "avg_playtime_forever")
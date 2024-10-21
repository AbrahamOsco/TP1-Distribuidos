from system.commonsSystem.node.grouperNode import GrouperNode
from system.commonsSystem.DTO.GamesDTO import STATE_REVIEWED

class Grouper(GrouperNode):
    def __init__(self):
        super().__init__(STATE_REVIEWED, 3, "reviews")
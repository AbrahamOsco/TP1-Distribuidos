import os
from system.commonsSystem.node.filterNode import FilterNode
from system.commonsSystem.DTO.GamesDTO import STATE_PLAYTIME
from system.commonsSystem.DTO.GenreDTO import GenreDTO

class Filter(FilterNode):
    def __init__(self):
        super().__init__(STATE_PLAYTIME)
        self.decade = int(os.getenv("DECADE"))

    def fulfills_criteria(self, element: GenreDTO):
        if len(element.release_date.split(', ')) < 2:
            return False
        year = int(element.release_date.split(', ')[1])
        return year >= self.decade and year < self.decade + 10
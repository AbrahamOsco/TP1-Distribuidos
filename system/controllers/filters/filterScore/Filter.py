from system.commonsSystem.node.filterNode import FilterNode
from system.commonsSystem.DTO.ReviewsDTO import STATE_TEXT
from system.commonsSystem.DTO.ReviewsDTO import ReviewMinimalDTO
import os

class Filter(FilterNode):
    def __init__(self):
        super().__init__(STATE_TEXT)
        self.score_wanted = int(os.getenv("SCORE_WANTED", 1))

    def fulfills_criteria(self, element: ReviewMinimalDTO):
        return element.review_score == self.score_wanted
from system.commonsSystem.node.filterNode import FilterNode
from system.commonsSystem.DTO.ReviewsDTO import STATE_IDNAME
from system.commonsSystem.DTO.ReviewsDTO import ReviewMinimalDTO
import langid

class Filter(FilterNode):
    def __init__(self):
        super().__init__(STATE_IDNAME)
        langid.set_languages(['en'])

    def fulfills_criteria(self, element: ReviewMinimalDTO):
        lang, _ = langid.classify(element.review_text)
        return lang == 'en'
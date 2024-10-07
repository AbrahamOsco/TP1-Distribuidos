
class TopN:

    def __init__(self, field_batch, field_to_compare, a_size):
        self.top_games = {}
        self.min_value_in_top = None
        self.id_with_min = None
        self.top_size = a_size
        self.field_batch = field_batch
        self.field_to_compare = field_to_compare
    
    def try_add_game(self, a_item):
        item_value = self.field_to_compare(a_item) 
        
        if len(self.top_games) < self.top_size :
            self.top_games[a_item.app_id] = (a_item.name, item_value)
            self.udpate_min()
        
        elif item_value > self.min_value_in_top:
            del self.top_games[self.id_with_min]
            self.top_games[a_item.app_id] = (a_item.name, item_value)
            self.udpate_min()

    def udpate_min(self):
        self.min_value_in_top = None
        for app_id, value in self.top_games.items():
            if self.min_value_in_top == None or self.min_value_in_top > value[1]:
                self.min_value_in_top = value[1]
                self.id_with_min = app_id

    def get_top10(self):
        top_items_sorted = sorted(self.top_games.values(), key = lambda  x: x[1], reverse =True)
        top_items_formated = {}
        for element in top_items_sorted:
            top_items_formated[element[0]] = element[1]
        return top_items_formated


    def update_top(self, a_batch):
        for game in self.field_batch(a_batch):
            self.try_add_game(game)


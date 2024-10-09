
class TopResults:

    def __init__(self, size):
        self.top_size = size
        self.top_data = {}
        self.id_with_min = None
        self.min_value_in_top = None
    
    def sort(self):
        sorted_top = sorted(self.top_data.items(), key =lambda element: element[1][1], reverse =True)
        sorted_top = {k: v for k, v in sorted_top} # pasamos la lista de tuplas a dic
        return sorted_top

    def try_to_insert_top(self, result_dto):
        for app_id, value in result_dto.data.items():
            if len(self.top_data) < self.top_size:
                self.top_data[app_id] = (value[0], value[1])
                self.udpate_min()
            elif value[1] > self.min_value_in_top:
                del self.top_data[self.id_with_min]
                self.top_data[app_id] = (value[0], value[1])
                self.min_value_in_top = None
                self.udpate_min()

    def udpate_min(self):
        for app_id, value in self.top_data.items():
            if self.min_value_in_top == None or self.min_value_in_top > value[1]:
                self.min_value_in_top = value[1]
                self.id_with_min = app_id


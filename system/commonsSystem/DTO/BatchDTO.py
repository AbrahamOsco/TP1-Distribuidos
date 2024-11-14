class BatchDTO:
    def __init__(self, client_id, global_counter):
        self.client_id = client_id
        self.global_counter = global_counter

    def is_EOF(self):
        return False
    
    def is_ok(self):
        return False
    
    def is_cancel(self):
        return False

    def is_commit(self):
        return False
    
    def is_reviews(self):
        return False
    
    def is_games(self):
        return False
    
    def serialize(self):
        pass

    def deserialize(data, offset):
        pass

    def get_amount(self):
        return 0
    
    def get_client(self):
        return self.client_id
    
    def set_state(self, state):
        pass
class EOFDTO:
    def __init__(self, client, confirmation=True):
        self.client = client
        self.confirmation = confirmation

    def to_string(self):
        return f"EOF|{self.client}|{int(self.confirmation)}"

    def from_string(data):
        data = data.split("|")
        return EOFDTO(data[1], data[2] == 1)
    
    def is_confirmation(self):
        return self.confirmation
import bisect

class IDList:
    def __init__(self, size: int=500):
        self.size = size
        self.values = []

    def insert(self, value):
        bisect.insort(self.values, value)
        if len(self.values) > self.size:
            self.values.pop(0)

    def already_processed(self, value):
        return value in self.values or (len(self.values) == self.size and value < self.values[0])
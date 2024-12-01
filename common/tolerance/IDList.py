import bisect

class IDList:
    def __init__(self, size: int=200):
        self.size = size
        self.values = []
        self.full = False

    def insert(self, value):
        bisect.insort(self.values, value)
        if len(self.values) > self.size:
            self.full = True
            self.values.pop(0)

    def already_processed(self, value):
        index = bisect.bisect_left(self.values, value)
        if index < len(self.values) and self.values[index] == value:
            return True
        return self.full and value < self.values[0]

    def to_bytes(self):
        ids_bytes = bytearray()
        ids_bytes.extend(len(self.values).to_bytes(2, byteorder='big'))
        for value in self.values:
            ids_bytes.extend(value.to_bytes(6, byteorder='big'))
        return bytes(ids_bytes)
    
    def from_bytes(self, data: bytes, offset: int):
        if len(data) < offset + 2:
            return offset
        size = int.from_bytes(data[offset:offset+2], byteorder='big')
        offset += 2
        for _ in range(size):
            value = int.from_bytes(data[offset:offset+6], byteorder='big')
            self.values.append(value)
            offset += 6
        self.full = len(self.values) == self.size
        return offset


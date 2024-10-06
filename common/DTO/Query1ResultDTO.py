OPERATION_TYPE_QUERY1 = 1

class Query1ResultDTO:
    def __init__(self, windows, linux, mac):
        self.operation_type = OPERATION_TYPE_QUERY1
        self.windows = windows
        self.linux = linux
        self.mac = mac
    
    def print(self):
        print("Result Query 1")
        print("windows: ", self.windows)
        print("linux: ", self.linux)
        print("mac: ", self.mac)
        print()
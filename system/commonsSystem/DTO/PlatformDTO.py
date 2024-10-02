OPERATION_TYPE_PLATFORM_DTO = 5

class PlatformDTO:
    def __init__(self, client_id: int, windows: int, mac: int, linux: int):
        self.operation_type = OPERATION_TYPE_PLATFORM_DTO
        self.client_id = client_id
        self.windows = windows
        self.mac = mac
        self.linux = linux
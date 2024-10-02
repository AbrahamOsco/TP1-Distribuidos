from system.commonsSystem.DTO.enums.OperationType import OperationType

class PlatformDTO:
    def __init__(self, client_id: int, windows: int, mac: int, linux: int):
        self.operation_type = OperationType.OPERATION_TYPE_PLATFORM_DTO
        self.client_id = client_id
        self.windows = windows
        self.mac = mac
        self.linux = linux

    def get_platform_count(self):
        return {
            "windows": self.windows,
            "mac": self.mac,
            "linux": self.linux
        }
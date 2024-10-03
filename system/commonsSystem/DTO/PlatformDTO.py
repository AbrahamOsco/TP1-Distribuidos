from system.commonsSystem.DTO.DTO import DTO
from system.commonsSystem.DTO.enums.OperationType import OperationType

class PlatformDTO(DTO):
    def __init__(self, client_id: int =0, windows: int =0, mac: int = 0, linux: int = 0):
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

    def serialize(self):
        platform_bytes = bytearray()
        platform_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        platform_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        platform_bytes.extend(self.windows.to_bytes(4, byteorder='big'))
        platform_bytes.extend(self.mac.to_bytes(4, byteorder='big'))
        platform_bytes.extend(self.linux.to_bytes(4, byteorder='big'))
        return bytes(platform_bytes)
    
    def deserialize(self, data, offset):
        operation_tpe = int.from_bytes(data[offset:offset + 1], byteorder='big')
        offset += 1
        client_id = int.from_bytes(data[offset:offset + 1], byteorder='big')
        offset += 1
        windows = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        mac = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        linux = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        return PlatformDTO(client_id =client_id, windows =windows, mac =mac, linux =linux), offset
    
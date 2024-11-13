from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from common.tolerance.checkpointFile import CheckpointFile
from common.tolerance.logFile import LogFile
from common.tolerance.IDList import IDList
from system.commonsSystem.node.structures.structure import Structure
from system.commonsSystem.node.routingPolicies.RoutingDefault import RoutingDefault
import os

class StatefullNode(Node):
    def __init__(self, data: Structure, id_lists: list[IDList]):
        self.data = data
        prefix = os.getenv("NODE_NAME") + os.getenv("NODE_ID") + "_"
        self.logs = LogFile(prefix)
        self.checkpoint = CheckpointFile(prefix, log_file=self.logs, id_lists=id_lists)
        super().__init__()
        self.recover()

    def recover(self):
        checkpoint, must_reprocess = self.checkpoint.load_checkpoint()
        self.data.from_bytes(checkpoint)
        if must_reprocess:
            for log in self.logs.logs:
                data = DetectDTO(log).get_dto()
                self.process_data(data)
        self.data.print_state()
        self.checkpoint.save_checkpoint(self.data.to_bytes())
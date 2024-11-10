import os
from common.tolerance.logFile import LogFile
from common.tolerance.IDList import IDList
import logging

PERSISTENT_VOLUME = "/persistent/"

class CheckpointFile:
    def __init__(self, identifier: str, log_file: LogFile=None, id_lists: list[IDList]=[]):
        self.identifier = identifier
        self.log_file = log_file
        self.id_lists = id_lists

    def _save_stg_checkpoint(self, data: bytes):
        file = open(PERSISTENT_VOLUME + self.identifier + "STG", "wb")
        self._serialize_id_lists(file)
        file.write(data)
        file.write("UNCORRUPTED END".encode())
        file.flush()
        os.fsync(file.fileno())
        file.close()

    def _serialize_id_lists(self, file):
        for id_list in self.id_lists:
            file.write(id_list.to_bytes())

    def _delete_dependant_files(self):
        if self.log_file is not None:
            self.log_file.reset()

    def _promote_stg_checkpoint(self):
        os.replace(PERSISTENT_VOLUME + self.identifier + "STG", PERSISTENT_VOLUME + self.identifier + "PRD")

    def _promote_staging_cleanup(self):
        self._delete_dependant_files()
        self._promote_stg_checkpoint()

    def save_checkpoint(self, data: bytes):
        self._save_stg_checkpoint(data)
        self._promote_staging_cleanup()
        logging.info("Checkpoint saved")

    def _verify_checkpoint_integrity(self, data: bytes) -> bool:
        return b"UNCORRUPTED END" in data
        
    def _verify_file_checkpoint_integrity(self, stage:str):
        file = open(PERSISTENT_VOLUME + self.identifier + stage, "rb")
        data = file.read()
        file.close()
        if not self._verify_checkpoint_integrity(data):
            return None

    def _delete_stg_checkpoint(self):
        try:
            os.remove(PERSISTENT_VOLUME + self.identifier + "STG")
        except FileNotFoundError:
            pass

    def _load_prd_checkpoint(self) -> bytes:
        file = open(PERSISTENT_VOLUME + self.identifier + "PRD", "rb")
        data = file.read()
        file.close()
        if not self._verify_checkpoint_integrity(data):
            logging.error("PRD checkpoint is corrupted")
            return None
        offset = 0
        for id_list in self.id_lists:
            offset = id_list.from_bytes(data, offset)
        return data[offset:].replace(b"UNCORRUPTED END", b"")

    def load_checkpoint(self) -> tuple[bytes, bool]:
        state = b""
        prd_checkpoint_exists = os.path.exists(PERSISTENT_VOLUME + self.identifier + "PRD")
        stg_checkpoint_exists = os.path.exists(PERSISTENT_VOLUME + self.identifier + "STG")
        if not prd_checkpoint_exists and not stg_checkpoint_exists:
            return state, True
        if stg_checkpoint_exists:
            if self._verify_file_checkpoint_integrity("STG"):
                self._promote_staging_cleanup()
                state = self._load_prd_checkpoint()
                return state, False
            else:
                self._delete_stg_checkpoint()
                state = self._load_prd_checkpoint()
                return state, True
        if not stg_checkpoint_exists:
            state = self._load_prd_checkpoint()
            return state, True
        return state, True
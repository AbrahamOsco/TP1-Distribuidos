import os

PERSISTENT_VOLUME = "/persistent/"

class TolerantFile:
    def __init__(self, identifier: str="default", dependant_files: list=[]):
        self.identifier = identifier
        self.dependant_files = dependant_files

    def _save_stg_checkpoint(self, data: bytes):
        file = open(PERSISTENT_VOLUME + self.identifier + "STG", "wb")
        file.write(data)
        file.write("UNCORRUPTED END".encode())
        file.close()

    def _delete_dependant_files(self):
        for file in self.dependant_files:
            try:
                os.remove(PERSISTENT_VOLUME + file)
            except FileNotFoundError:
                pass

    def _delete_prd_checkpoint(self):
        try:
            os.remove(PERSISTENT_VOLUME + self.identifier + "PRD")
        except FileNotFoundError:
            pass

    def _promote_stg_checkpoint(self):
        os.rename(PERSISTENT_VOLUME + self.identifier + "STG", PERSISTENT_VOLUME + self.identifier + "PRD")

    def _promote_staging_cleanup(self):
        self._delete_prd_checkpoint()
        self._delete_dependant_files()
        self._promote_stg_checkpoint()

    def save_checkpoint(self, data: bytes):
        self._save_stg_checkpoint(data)
        self._promote_staging_cleanup()

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
            return None
        return data.replace(b"UNCORRUPTED END", b"")

    def load_checkpoint(self) -> tuple[bytes, bool]:
        state = None
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
        return None, True
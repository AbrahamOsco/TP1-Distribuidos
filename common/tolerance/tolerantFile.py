import os

class TolerantFile:
    def __init__(self, identifier: str="default", dependant_files: list=[]):
        self.identifier = identifier
        self.dependant_files = dependant_files

    def _save_stg_checkpoint(self, data: bytes):
        file = open(self.identifier + "STG", "wb")
        file.write(data)
        file.write("UNCORRUPTED END".encode())
        file.close()

    def _delete_dependant_files(self):
        for file in self.dependant_files:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass

    def _delete_prd_checkpoint(self):
        try:
            os.remove(self.identifier + "PRD")
        except FileNotFoundError:
            pass

    def _promote_stg_checkpoint(self):
        os.rename(self.identifier + "STG", self.identifier + "PRD")

    def save_checkpoint(self, data: bytes):
        self._save_stg_checkpoint(data)
        self._delete_prd_checkpoint()
        self._delete_dependant_files()
        self._promote_stg_checkpoint()

    def _verify_checkpoint_integrity(self, data: bytes) -> bool:
        return b"UNCORRUPTED END" in data
        
    def _verify_file_checkpoint_integrity(self, stage:str):
        file = open(self.identifier + stage, "rb")
        data = file.read()
        file.close()
        if not self._verify_checkpoint_integrity(data):
            return None

    def load_checkpoint(self) -> bytes:
        prd_checkpoint_exists = os.path.exists(self.identifier + "PRD")
        stg_checkpoint_exists = os.path.exists(self.identifier + "STG")
        if not prd_checkpoint_exists and not stg_checkpoint_exists:
            return None
        if stg_checkpoint_exists: 
            if self._verify_file_checkpoint_integrity("STG"):
                self._delete_prd_checkpoint()
                self._delete_dependant_files()
                self._promote_stg_checkpoint()
                #LOAD STG
            else:
                self._delete_stg_checkpoint()
                #LOAD PRD AND REPROCESS
            return
        if not stg_checkpoint_exists and self._verify_file_checkpoint_integrity("PRD"):
            #LOAD PRD AND REPROCESS
            self.save_checkpoint()
            return
        return None
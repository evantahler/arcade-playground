import hashlib
import tempfile
from abc import ABC, abstractmethod
from contextlib import contextmanager


class ObjectStorage(ABC):
    @abstractmethod
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        pass

    @abstractmethod
    def download_file(self, remote_path: str, local_path: str) -> bool:
        pass

    @abstractmethod
    def delete_remote_file(self, remote_path: str) -> bool:
        pass

    def get_remote_hash(self, remote_path: str) -> str:
        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            self.download_file(remote_path, tmp.name)
            with open(tmp.name, "rb") as f:
                _hash = hashlib.md5(f.read()).hexdigest()  # noqa: S324
        return _hash

    def get_local_hash(self, local_path: str) -> str:
        with open(local_path, "rb") as f:
            _hash = hashlib.md5(f.read()).hexdigest()  # noqa: S324
        return _hash

    @contextmanager
    def with_locked_and_downloaded_file(
        self,
        remote_path: str,
    ):
        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            downloaded = self.download_file(remote_path, tmp.name)
            if downloaded:
                local_hash = self.get_local_hash(tmp.name)

            with open(tmp.name, "rb") as f:
                yield f

            remote_hash = self.get_remote_hash(remote_path)
            if downloaded and local_hash != remote_hash:
                error_message = f"File {remote_path} has changed on remote storage between the time it was downloaded and the time it was uploaded"  # noqa: E501
                raise ValueError(error_message)

            self.upload_file(tmp.name, remote_path)

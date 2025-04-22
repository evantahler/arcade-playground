import boto3
import botocore
import botocore.exceptions

from arcade_rag.object_storage import ObjectStorage


class S3ObjectStorage(ObjectStorage):
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        region_name: str,
    ):
        self.client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name,
        )
        self.bucket_name = bucket_name

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        self.client.upload_file(
            Filename=local_path,
            Bucket=self.bucket_name,
            Key=remote_path,
        )
        return True

    def download_file(self, remote_path: str, local_path: str) -> bool:
        try:
            self.client.download_file(
                Filename=local_path,
                Bucket=self.bucket_name,
                Key=remote_path,
            )
        except botocore.exceptions.ClientError as error:
            if error.response.get("Error", {}).get("Code") == "404":
                return False
            raise error  # noqa: TRY201
        return True

    def delete_remote_file(self, remote_path: str) -> bool:
        self.client.delete_object(Bucket=self.bucket_name, Key=remote_path)
        return True

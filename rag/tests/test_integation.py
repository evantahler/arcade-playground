import os

from arcade_rag.object_storages.s3 import S3ObjectStorage

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")
RAG_DATABASE_FILE = os.getenv("RAG_DATABASE_FILE")


def test_integration():
    if (
        not AWS_ACCESS_KEY
        or not AWS_SECRET_KEY
        or not AWS_BUCKET_NAME
        or not AWS_REGION
        or not RAG_DATABASE_FILE
        or not RAG_DATABASE_FILE
    ):
        error_message = "Missing environment variables"
        raise ValueError(error_message)

    object_storage = S3ObjectStorage(
        access_key=AWS_ACCESS_KEY,
        secret_key=AWS_SECRET_KEY,
        bucket_name=AWS_BUCKET_NAME,
        region_name=AWS_REGION,
    )

    with object_storage.with_locked_and_downloaded_file(RAG_DATABASE_FILE) as f:
        assert f is not None

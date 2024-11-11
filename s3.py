from io import BytesIO
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from typing import Optional
import os

class _MinioClient:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket_name: str):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )

    def save(self, data: bytes, object_name: Optional[str]) -> bool:
        """Save a bytes object to the S3 bucket."""
        if object_name is None:
            raise ValueError("Object name must be provided")
        try:
            self.s3_client.upload_fileobj(BytesIO(data), self.bucket_name, f'/tmp/{object_name}')
            return True
        except (NoCredentialsError, PartialCredentialsError) as e:
            print(f"Error uploading file: {e}")
            return False

    def download(self, object_name: str) -> dict:
        """Download a single file from the S3 bucket and return it as a FileResponse for FastAPI."""
        file_path = f"/tmp/{object_name}"
        file = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_path)
        return {
                "file_name": object_name,
                "path": file_path,
                "content": file, 
            }
        

    def download_multiple(self, object_names: list[str]) -> list[dict]:
        """Download multiple files from the S3 bucket"""
        responses = []
        for object_name in object_names:
            file_path = f"/tmp/{object_name}"
            file = self.s3_client.get_object(Bucket=self.bucket_name, Key=object_name)
            file_dict = {
                "file_name": object_name,
                "path": file_path,
                "content": file, 
            }
            responses.append(file_dict)
        return responses

MinioClient = _MinioClient(
    endpoint=os.environ["MINIO_ENDPOINT"],
    access_key=os.environ["MINIO_ACCESS_KEY"],
    secret_key=os.environ["MINIO_SECRET_KEY"],
    bucket_name=os.environ["MINIO_BUCKET_NAME"],
)
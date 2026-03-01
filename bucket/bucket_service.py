import os
import uuid

import boto3
from botocore.exceptions import ClientError
from openai.types.images_response import ImagesResponse

class BucketService:
    def __init__(self):
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "files")
        endpoint_url = os.getenv("S3_ENDPOINT_URL")
        region_name = os.getenv("AWS_REGION", "us-east-1")
        access_key = os.getenv("AWS_ACCESS_KEY_ID", "local")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "local")

        self.amazon_s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            region_name=region_name,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        try:
            self.amazon_s3.head_bucket(Bucket=self.bucket_name)
            return
        except ClientError:
            pass

        # us-east-1 does not allow LocationConstraint in create_bucket.
        if self.amazon_s3.meta.region_name == "us-east-1":
            self.amazon_s3.create_bucket(Bucket=self.bucket_name)
        else:
            self.amazon_s3.create_bucket(
                Bucket=self.bucket_name,
                CreateBucketConfiguration={"LocationConstraint": self.amazon_s3.meta.region_name},
            )

    def store_file(self, file_content: bytes) -> str:
        file_id = f"{uuid.uuid4().hex}.bin"
        self.amazon_s3.put_object(Bucket=self.bucket_name, Key=file_id, Body=file_content)
        return file_id

    

    def delete_file(self, file_id: str) -> None:
        self.amazon_s3.delete_object(Bucket=self.bucket_name, Key=file_id)

    def save_image_from_image_response(self, image_response: ImagesResponse) -> str:
        return self.store_file(image_response.data[0].b64_json)
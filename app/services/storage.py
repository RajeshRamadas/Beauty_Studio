import hashlib
import hmac
import os
import time
from typing import Optional
from app.core.config import settings
from app.core.logging import logger

class StorageService:
    def __init__(self, storage_type: Optional[str] = None):
        self.storage_type = storage_type or settings.STORAGE_TYPE

    def save_image(self, key: str, data: bytes) -> str:
        """Save image bytes to local disk storage or Amazon S3 object storage."""
        if self.storage_type == "s3" and settings.AWS_ACCESS_KEY_ID:
            try:
                import boto3
                s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION,
                )
                s3_client.put_object(
                    Bucket=settings.S3_BUCKET_NAME,
                    Key=key,
                    Body=data,
                    ContentType="image/png" if key.endswith(".png") else "image/jpeg",
                )
                return f"s3://{settings.S3_BUCKET_NAME}/{key}"
            except Exception as exc:
                logger.error("Failed uploading to S3 (%s), falling back to local: %s", key, exc)

        # Local filesystem storage
        base_dir = os.path.dirname(os.path.join("storage", key))
        os.makedirs(base_dir, exist_ok=True)
        path = os.path.join("storage", key)
        with open(path, "wb") as f:
            f.write(data)
        return path

    def get_signed_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a short-lived authorized URL for accessing an image asset."""
        if self.storage_type == "s3" and settings.AWS_ACCESS_KEY_ID:
            try:
                import boto3
                s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION,
                )
                return s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": settings.S3_BUCKET_NAME, "Key": key},
                    ExpiresIn=expires_in,
                )
            except Exception:
                pass
            return f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{key}?Expires={expires_in}"

        expires = int(time.time()) + expires_in
        return f"{settings.API_V1_STR}/images/{key}?exp={expires}&sig={sign(key, expires)}"

    def delete(self, key: str) -> None:
        """Delete a stored image (local or S3). Missing files are ignored."""
        if self.storage_type == "s3" and settings.AWS_ACCESS_KEY_ID:
            try:
                import boto3
                boto3.client(
                    "s3",
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION,
                ).delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
            except Exception as exc:
                logger.error("Failed deleting %s from S3: %s", key, exc)
        path = os.path.join("storage", key)
        try:
            if os.path.isfile(path):
                os.remove(path)
        except OSError as exc:
            logger.error("Failed deleting %s: %s", path, exc)


def sign(key: str, expires: int) -> str:
    """HMAC signature for a short-lived local image URL."""
    msg = f"{key}:{expires}".encode()
    return hmac.new(settings.SECRET_KEY.encode(), msg, hashlib.sha256).hexdigest()[:32]


def verify(key: str, expires: int, signature: str) -> bool:
    return expires >= time.time() and hmac.compare_digest(sign(key, expires), signature or "")


storage_service = StorageService()

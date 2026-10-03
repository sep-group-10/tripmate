import io
import logging
import os
import uuid
from urllib.parse import urlsplit

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import UploadFile
from PIL import Image, ImageOps

from app.core.errors import ApiError, ErrorCode

logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_DIMENSION = 1600
JPEG_QUALITY = 85


def _resize_image(raw_bytes: bytes) -> bytes:
    """Strip EXIF, flatten to RGB, downscale if larger than MAX_DIMENSION
    on the long edge, and re-encode as JPEG. Never upscales."""
    try:
        image = Image.open(io.BytesIO(raw_bytes))
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
    except Exception as exc:
        raise ApiError(ErrorCode.VALIDATION_ERROR, "File is not a valid image") from exc

    if max(image.size) > MAX_DIMENSION:
        image.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

    output = io.BytesIO()
    image.save(output, format="JPEG", quality=JPEG_QUALITY)
    return output.getvalue()


def upload_image(file: UploadFile, key_prefix: str) -> str:
    """Validate, resize, and store an uploaded image in S3, returning the
    CloudFront URL it is served from (never the raw S3 URL - the bucket
    is private and only reachable through CloudFront's OAC)."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ApiError(
            ErrorCode.VALIDATION_ERROR,
            "Only JPEG, PNG, and WebP images are allowed",
        )

    raw_bytes = file.file.read()
    if len(raw_bytes) > MAX_UPLOAD_BYTES:
        raise ApiError(ErrorCode.VALIDATION_ERROR, "Image must be 8MB or smaller")
    if not raw_bytes:
        raise ApiError(ErrorCode.VALIDATION_ERROR, "Image file is empty")

    resized_bytes = _resize_image(raw_bytes)

    bucket = os.getenv("AWS_S3_BUCKET")
    region = os.getenv("AWS_S3_REGION")
    cloudfront_domain = os.getenv("AWS_CLOUDFRONT_DOMAIN")

    if not bucket or not region or not cloudfront_domain:
        logger.error("S3/CloudFront environment variables are not configured")
        raise ApiError(
            ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE,
            "Image storage is not available right now",
        )

    key = f"{key_prefix}/{uuid.uuid4()}.jpg"
    client = boto3.client("s3", region_name=region)

    try:
        client.put_object(
            Bucket=bucket,
            Key=key,
            Body=resized_bytes,
            ContentType="image/jpeg",
        )
    except (BotoCoreError, ClientError):
        logger.exception("Failed to upload image to S3: key=%s", key)
        raise ApiError(
            ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE,
            "Image storage is not available right now",
        ) from None

    return f"https://{cloudfront_domain}/{key}"


def delete_image(url: str, key_prefix: str) -> None:
    """Delete one image only when its URL belongs to this app's CDN and
    the requested entity's upload directory."""
    bucket = os.getenv("AWS_S3_BUCKET")
    region = os.getenv("AWS_S3_REGION")
    cloudfront_domain = os.getenv("AWS_CLOUDFRONT_DOMAIN")
    if not bucket or not region or not cloudfront_domain:
        logger.error("S3/CloudFront environment variables are not configured")
        raise ApiError(
            ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE,
            "Image storage is not available right now",
        )

    parsed = urlsplit(url)
    expected_domain = (
        cloudfront_domain.removeprefix("https://").removeprefix("http://").rstrip("/")
    )
    expected_prefix = f"/{key_prefix}/"
    filename = (
        parsed.path[len(expected_prefix) :]
        if parsed.path.startswith(expected_prefix)
        else ""
    )
    try:
        uuid.UUID(filename.removesuffix(".jpg"))
    except (ValueError, AttributeError):
        filename = ""
    if (
        parsed.scheme != "https"
        or parsed.netloc != expected_domain
        or parsed.query
        or parsed.fragment
        or not filename.endswith(".jpg")
        or "/" in filename
    ):
        raise ApiError(ErrorCode.VALIDATION_ERROR, "Invalid photo URL")

    client = boto3.client("s3", region_name=region)
    try:
        client.delete_object(Bucket=bucket, Key=f"{key_prefix}/{filename}")
    except (BotoCoreError, ClientError):
        logger.exception(
            "Failed to delete image from S3: key=%s/%s", key_prefix, filename
        )
        raise ApiError(
            ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE,
            "Image storage is not available right now",
        ) from None

"""S3-compatible object storage helpers for the RetailPulse data lake."""

from pathlib import Path

import boto3
from botocore.config import Config

from retailpulse.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.seaweed_s3_endpoint,
        aws_access_key_id=settings.seaweed_access_key,
        aws_secret_access_key=settings.seaweed_secret_key,
        region_name="us-east-1",
        config=Config(s3={"addressing_style": "path"}),
    )


def ensure_bucket() -> None:
    client = get_s3_client()
    buckets = {bucket["Name"] for bucket in client.list_buckets().get("Buckets", [])}
    if settings.seaweed_bucket not in buckets:
        client.create_bucket(Bucket=settings.seaweed_bucket)


def put_object(key: str, body: bytes) -> None:
    ensure_bucket()
    get_s3_client().put_object(Bucket=settings.seaweed_bucket, Key=key, Body=body)


def get_object(key: str) -> bytes:
    response = get_s3_client().get_object(Bucket=settings.seaweed_bucket, Key=key)
    return response["Body"].read()


def list_objects(prefix: str = "") -> list[str]:
    ensure_bucket()
    keys: list[str] = []
    paginator = get_s3_client().get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=settings.seaweed_bucket, Prefix=prefix):
        keys.extend(item["Key"] for item in page.get("Contents", []))
    return keys


def download_objects(prefix: str, destination: Path) -> list[Path]:
    destination.mkdir(parents=True, exist_ok=True)
    downloaded: list[Path] = []
    for key in list_objects(prefix):
        relative = key[len(prefix):].lstrip("/")
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(get_object(key))
        downloaded.append(target)
    return downloaded

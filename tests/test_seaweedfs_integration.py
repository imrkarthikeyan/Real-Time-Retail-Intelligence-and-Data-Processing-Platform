import boto3
import pytest
from botocore.exceptions import EndpointConnectionError

from retailpulse.config import settings


@pytest.fixture
def s3():
    client = boto3.client(
        "s3",
        endpoint_url=settings.seaweed_s3_endpoint,
        aws_access_key_id=settings.seaweed_access_key,
        aws_secret_access_key=settings.seaweed_secret_key,
        region_name="us-east-1",
    )
    try:
        client.list_buckets()
    except EndpointConnectionError:
        pytest.skip("SeaweedFS is not reachable")
    return client


def test_seaweedfs_bucket_object_round_trip(s3):
    bucket = settings.seaweed_bucket
    names = {item["Name"] for item in s3.list_buckets().get("Buckets", [])}
    assert bucket in names

    key = "integration/test.txt"
    body = b"RetailPulse SeaweedFS integration test"
    s3.put_object(Bucket=bucket, Key=key, Body=body)

    listed = s3.list_objects_v2(Bucket=bucket, Prefix="integration/")
    assert key in {item["Key"] for item in listed.get("Contents", [])}
    downloaded = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    assert downloaded == body


def test_seaweedfs_persists_expected_lake_prefixes(s3):
    bucket = settings.seaweed_bucket
    for prefix in ("bronze/orders", "silver/orders", "quarantine/orders",
                   "gold/daily_sales"):
        s3.put_object(
            Bucket=bucket,
            Key=f"{prefix}/integration-placeholder",
            Body=b"",
        )
        result = s3.list_objects_v2(Bucket=bucket, Prefix=f"{prefix}/")
        assert result.get("Contents")

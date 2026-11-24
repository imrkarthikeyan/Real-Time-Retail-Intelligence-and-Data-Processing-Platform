$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

$pythonCode = @'
from retailpulse.storage import ensure_bucket, get_s3_client, settings

ensure_bucket()
client = get_s3_client()
key = "smoke/test.txt"
client.put_object(Bucket=settings.seaweed_bucket, Key=key, Body=b"RetailPulse SeaweedFS smoke test")
keys = [item["Key"] for item in client.list_objects_v2(Bucket=settings.seaweed_bucket, Prefix="smoke/").get("Contents", [])]
body = client.get_object(Bucket=settings.seaweed_bucket, Key=key)["Body"].read()
print(f"Bucket: {settings.seaweed_bucket}")
print(f"Objects: {keys}")
print(f"Downloaded: {body.decode('utf-8')}")
'@
$tempScript = Join-Path $env:TEMP "retailpulse-seaweedfs-smoke.py"
$pythonCode | Set-Content -Path $tempScript -Encoding utf8
& .\.venv\Scripts\python.exe $tempScript

import aioboto3
from botocore.exceptions import ClientError
from sentry_sdk import capture_exception
from config import log, settings as st


async def generate_presigned_url(
    key: str, content_type: str = None, expires_in: int = 900
) -> str:
    try:
        session = aioboto3.Session()
        async with session.client(
            "s3",
            region_name=st.AWS_REGION,
            aws_access_key_id=st.ACCESS_KEY_ID,
            aws_secret_access_key=st.ACCESS_SECRET_KEY,
        ) as s3_client:
            params = {"Bucket": st.AWS_S3_BUCKET, "Key": key}
            if content_type:
                params["ContentType"] = content_type

            url = await s3_client.generate_presigned_url(
                ClientMethod="put_object",
                Params=params,
                ExpiresIn=expires_in,
            )
            return url
    except ClientError as e:
        capture_exception(e)
        log.exception(f"generate presigned url error: {e}")
        raise

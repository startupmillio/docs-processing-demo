from uuid import uuid4

from fastapi import APIRouter
from fastapi import (
    Depends,
    HTTPException,
)
from sqlalchemy.ext.asyncio import AsyncSession
from services.s3 import generate_presigned_url as gen_presigned_url
from auth.auth0 import get_current_user
import models as m
import sqlalchemy as sa
from db import get_session_dep


upload_router = APIRouter(prefix="/upload", tags=["upload"])


@upload_router.get("/generate-presigned-url")
async def generate_presigned_url(
    user=Depends(get_current_user),
    db: AsyncSession = get_session_dep,
    content_type: str = None,
):
    s3_key = str(uuid4())
    url = await gen_presigned_url(s3_key, content_type=content_type)
    if not url:
        raise HTTPException(status_code=500, detail="Failed to generate presigned URL")

    await db.scalar(
        sa.insert(m.AudioFile).values(
            {
                m.AudioFile.user_id: user["sub"],
                m.AudioFile.s3_key: s3_key,
            }
        )
    )

    return {"url": url, "s3_key": s3_key}

import sqlalchemy as sa
from typing import Optional

import models as m
from fastapi import APIRouter, HTTPException, Depends
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from api.exceptions import BadRequestException, ForbiddenException, NotFoundException
from api.schemas import (
    TranscriptionResult,
    TranscriptionRequest,
    TranscriptionResponse,
    TranscriptionTaskStatus,
)
from config import log
from db import get_session_dep
from tasks.transcribe_audio import transcribe_audio_task
from auth.auth0 import get_current_user

transcribe_router = APIRouter(prefix="/transcribe")


@transcribe_router.post("/", response_model=TranscriptionResponse)
async def start_transcription(
    req: TranscriptionRequest,
    user=Depends(get_current_user),
    db: AsyncSession = get_session_dep,
):
    s3_key = await db.scalar(
        sa.select(m.AudioFile.s3_key).where(
            m.AudioFile.s3_key == req.s3_key,
            m.AudioFile.user_id == user["sub"],
        )
    )

    if not s3_key:
        raise ForbiddenException(
            message="File does not exist or you dont have permissions"
        )

    meeting_id = req.meeting_id or str(uuid4())
    log.info("received_message")
    try:
        task = transcribe_audio_task.delay(s3_key, meeting_id, user["sub"])
        await db.execute(
            sa.insert(m.Task).values(
                {
                    m.Task.celery_task_id: task.id,
                    m.Task.status: "CREATED",
                    m.Task.user_id: user["sub"],
                }
            )
        )
        log.info("stored_message")
        return {"task_id": task.id, "meeting_id": meeting_id}
    except Exception as e:
        log.exception(f"Exception during task creation: {e}")
        raise HTTPException(status_code=500, detail=f"Task dispatch failed")


@transcribe_router.get("/status/{task_id}", response_model=TranscriptionTaskStatus)
async def get_transcription_status(
    task_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = get_session_dep,
):
    task = (
        await db.execute(
            sa.select(
                m.Task.id,
                m.Task.status,
            ).where(
                sa.and_(
                    m.Task.celery_task_id == task_id,
                    m.Task.user_id == user["sub"],
                )
            )
        )
    ).fetchone()
    if not task:
        raise BadRequestException(f"Task {task_id} not found")

    return {"task_id": task_id, "status": task.status}


@transcribe_router.get(
    "/results/{meeting_id}", response_model=Optional[TranscriptionResult]
)
async def get_transcription_by_meeting(
    meeting_id: str, user=Depends(get_current_user), db: AsyncSession = get_session_dep
):
    query = (
        sa.select(m.Transcription)
        .where(
            m.Transcription.meeting_id == meeting_id,
            m.Transcription.user_id == user["sub"],
        )
        .order_by(m.Transcription.record_created.desc())
        .limit(1)
    )
    result = (await db.execute(query)).scalar_one_or_none()
    if not result:
        raise NotFoundException(f"Meeting {meeting_id} not found")
    return result

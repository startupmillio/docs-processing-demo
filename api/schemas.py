from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class TranscriptionResult(BaseModel):
    id: int
    meeting_id: str
    text: Optional[str] = None
    summary: Optional[str] = None
    record_created: datetime

    class Config:
        orm_mode = True


class TranscriptionRequest(BaseModel):
    s3_key: str
    meeting_id: Optional[str] = None


class TranscriptionTaskStatus(BaseModel):
    task_id: str
    status: str


class TranscriptionResponse(BaseModel):
    task_id: str
    meeting_id: str

    class Config:
        schema_extra = {
            "example": {
                "task_id": "ce05212e-7a1a-4f26-a8cb-9f9f56d4d643",
                "meeting_id": "fbbf4db0-88bb-4eb0-8023-9f9d8969b194",
            }
        }

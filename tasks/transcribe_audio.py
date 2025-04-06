import asyncio
import json
import subprocess
import tempfile
import wave
from pathlib import Path
from typing import Optional

import boto3
import sqlalchemy as sa
from celery import Celery
from sqlalchemy.orm import Session
from vosk import KaldiRecognizer, Model

import models as m
from config import log, settings as st
from db import sync_engine
from services.summarizer import summarize_long_text


celery_app = Celery("transcribe_audio", broker=st.BROKER_URL)


s3 = boto3.client(
    "s3",
    aws_access_key_id=st.ACCESS_KEY_ID,
    aws_secret_access_key=st.ACCESS_SECRET_KEY,
)


model = Model("vosk-model-small-en-us-0.15")


def download_from_s3(s3_key: str) -> Path:
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    s3.download_fileobj(st.AWS_S3_BUCKET, s3_key, tmp_file)
    return Path(tmp_file.name)


def convert_to_wav(input_path: Path) -> Path:
    output_path = input_path.with_suffix(".converted.wav")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-ar",
            "16000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            "-f",
            "wav",
            str(output_path),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return output_path


def transcribe_audio_file(wav_path: Path) -> str:
    with wave.open(str(wav_path), "rb") as wf:
        if (
            wf.getnchannels() != 1
            or wf.getsampwidth() != 2
            or wf.getframerate() != 16000
        ):
            raise ValueError("Audio file must be 16kHz mono PCM.")

        recognizer = KaldiRecognizer(model, wf.getframerate())
        recognizer.SetWords(True)

        full_text = []
        while data := wf.readframes(4000):
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                full_text.append(result.get("text", ""))

        final_result = json.loads(recognizer.FinalResult())
        full_text.append(final_result.get("text", ""))

        return ". ".join(filter(None, full_text))


def update_task_status(session: Session, task_id: str, status: str):
    session.execute(
        sa.update(m.Task)
        .where(m.Task.celery_task_id == task_id)
        .values({m.Task.status: status})
    )


def cleanup_files(*paths: Optional[Path]):
    for path in paths:
        try:
            if path and path.exists():
                path.unlink()
        except Exception as e:
            log.exception(f"[CLEANUP ERROR] Failed to delete {path}: {e}")


# === Main Process with Shared Session ===


def process_transcription_with_session(
    s3_key: str, meeting_id: str, user_id: str, task_id: str
):
    original_path: Optional[Path] = None
    wav_path: Optional[Path] = None

    with Session(sync_engine) as session:
        try:
            update_task_status(session, task_id, "PROCESSING")
            session.commit()

            original_path = download_from_s3(s3_key)
            wav_path = convert_to_wav(original_path)
            log.info("Audio converted to WAV format")

            text = transcribe_audio_file(wav_path)
            log.info("Transcription complete")

            summary = asyncio.run(summarize_long_text(text))

            session.execute(
                sa.insert(m.Transcription).values(
                    user_id=user_id,
                    meeting_id=meeting_id,
                    text=text,
                    summary=summary,
                )
            )
            update_task_status(session, task_id, "FINISHED")
            session.commit()

            log.info("Task finished successfully")

        except Exception as e:
            log.exception(f"[TASK ERROR] {e}")
            try:
                update_task_status(session, task_id, "FAILED")
                session.commit()
            except Exception as update_err:
                log.exception(
                    f"[STATUS UPDATE ERROR] Could not mark task as FAILED: {update_err}"
                )

        finally:
            cleanup_files(original_path, wav_path)


@celery_app.task(name="transcribe_audio")
def transcribe_audio_task(s3_key: str, meeting_id: str, user_id: str):
    task_id = transcribe_audio_task.request.id
    log.info(f"Starting transcription task {task_id}")
    process_transcription_with_session(s3_key, meeting_id, user_id, task_id)

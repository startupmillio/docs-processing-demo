import json

import sqlalchemy as sa
from vosk import Model, KaldiRecognizer
from resemblyzer import VoiceEncoder
from sentry_sdk import capture_exception
from sqlalchemy.ext.asyncio import AsyncSession

import models as m
from db import persistent_engine
from config import log
from services.summarizer import summarize_long_text

model = Model("vosk-model-small-en-us-0.15")
encoder = VoiceEncoder()


async def save_transcription_to_db(user_id: str, meeting_id: str, text: str):
    try:
        summary = await summarize_long_text(text)
        async with AsyncSession(persistent_engine) as session, session.begin():
            await session.execute(
                sa.insert(m.Transcription).values(
                    user_id=user_id,
                    meeting_id=str(meeting_id),
                    text=text.strip(),
                    summary=summary,
                )
            )
        log.info(f"{meeting_id=} transcription and summary saved")
    except Exception as e:
        capture_exception(e)
        log.exception(f"DB_ERROR: {e}")
        raise


async def handle_audio_message(
    message: bytes, recognizer: KaldiRecognizer
) -> tuple[str, str]:
    if recognizer.AcceptWaveform(message):
        result = json.loads(recognizer.Result())
        final_text = result.get("text", "")
        return final_text, ""
    else:
        partial_result = json.loads(recognizer.PartialResult())
        partial_text = partial_result.get("partial", "")
        return "", partial_text


async def live_transcription_generator(websocket, user_id: str, meeting_id: str):
    log.info(f"Start transcribing {meeting_id=}")
    recognizer = KaldiRecognizer(model, 16000)
    final_results = []

    try:
        async for message in websocket.iter_bytes():
            final_text, partial_text = await handle_audio_message(message, recognizer)

            if final_text:
                final_results.append(final_text.capitalize())
                log.info(f"final: {final_text}")
                await websocket.send_text(
                    json.dumps({"type": "final", "text": final_text})
                )
            elif partial_text:
                log.info(f"partial: {partial_text}")
                await websocket.send_text(
                    json.dumps({"type": "partial", "text": partial_text})
                )

    finally:
        full_text = ". ".join(final_results) + ("." if final_results else "")
        await save_transcription_to_db(user_id, meeting_id, full_text)

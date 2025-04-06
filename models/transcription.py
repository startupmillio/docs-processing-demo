import sqlalchemy as sa
from models.base import Model, RecordTimestampFields


class Transcription(Model, RecordTimestampFields):
    __tablename__ = "transcriptions"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Text, nullable=False)
    meeting_id = sa.Column(sa.Text, nullable=True)
    text = sa.Column(sa.Text)
    summary = sa.Column(sa.Text)

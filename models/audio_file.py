import sqlalchemy as sa

from models.base import Model, RecordTimestampFields


class AudioFile(Model, RecordTimestampFields):
    __tablename__ = "audio_files"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Text, nullable=False)
    s3_key = sa.Column(sa.Text, nullable=False)
    filename = sa.Column(sa.Text)

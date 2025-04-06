import sqlalchemy as sa
from models.base import Model, RecordTimestampFields


class Task(Model, RecordTimestampFields):
    __tablename__ = "tasks"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    celery_task_id = sa.Column(sa.Text, nullable=False)
    status = sa.Column(sa.Text, nullable=False)
    user_id = sa.Column(sa.Text, nullable=False)

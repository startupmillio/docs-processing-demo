FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg build-essential curl git libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN pip install pipenv
COPY Pipfile Pipfile.lock /app/
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu && pipenv install --deploy --system

COPY . .

RUN rm -f .secrets.toml

ENV ENV_FOR_DYNACONF="default"

EXPOSE 8000

CMD ["bash", "-c", "alembic upgrade head && python main.py"]

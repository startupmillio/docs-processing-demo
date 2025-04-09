# 🎙️ Audio Processing Demo

A live transcription demo powered by Vosk, WebSockets, Auth0 and OpenAI.

## 📚 API Documentation

Explore the full API via interactive Swagger UI:  
👉 [API Docs](https://audio-processing-demo.click/docs#/)

> ⚠️ **Authentication Required**  
> All endpoints require cookie-based Auth0 login. Without proper authentication, requests will return a **401 Unauthorized** error.

---

## 🔐 Authentication

Login here to get started:  
🔗 [Login Page](https://audio-processing-demo.click/auth/login)

- Auth0-based authentication
- You can create a new account
- Once logged in, you'll be redirected to the main app

Logout when done:  
🔗 [Logout](https://audio-processing-demo.click/auth/logout)

---

## 🧠 Main Application

🔗 [Live Transcription App](https://audio-processing-demo.click/)

- Real-time audio transcription via **WebSockets**
- Auto-generates and inserts `meeting-id` in requests
- Transcripts and summaries are fetched based on this ID

> ⚠️ Frontend is rough — built only for demo purposes..

---

## 📁 File Upload

🔗 [Upload Audio File](https://audio-processing-demo.click/upload-file)

- Upload files using a `presigned_link`
- Simple and minimal UI for quick testing

---

## 📝 Transcription Workflow

1. **Start a Transcription Task**  
   `POST` to [`/transcribe/`](https://audio-processing-demo.click/docs/)  
   Submit your `s3key` to initiate transcript & summary generation.

2. **Check Task Status**  
   `GET`:   `/transcribe/task/{task_id}`

3. **Fetch Transcript & Summary**  
   `GET`:   `/transcribe/result/{meeting_id}`

---

## Setting up

### Prerequisites

Before proceeding, ensure you have the following tools installed and configured:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [AWS access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html)
- [OpenAi ApiKey](https://platform.openai.com/api-keys)
- [Postgresql](https://www.postgresql.org/) (to run locally)
- [Redis](https://redis.io/) (to run locally)

### Auth0 App settings
1. Go to Auth0 official site and login there
2. Go to the `Applications` tab, `+Create Application` button, choose Regular Web Application. Create one
3. Go to `Settings`. here you'll see your `AUTH0_DOMAIN_NAME`, `AUTH0_CLIENT_ID`, `AUTH0_CLIENT_SECRET`. 
4. In the `Application URIs` section in `Allowed Callback URLs` paste `{ur_domain_name}/auth/callback`, in `Allowed LoaOur URLs` -> `{ur_domain_name}/auth/login`
5. Scroll down to `Advanced settings`. There go to `Grant Types` and add `Authorization code` option
6. Save
7. Go to the `APIs` tab, `+Create API` button, `Identifier` -> `URL_DOMAIN_NAME` -> Save

### Running the app locally

1. Setup a virtualenv using python3.11
2. pip install pipenv
3. pipenv install
4. copy `.secrets.toml.example` as `.secrets.toml` and replace placeholders with your variables
5. `alembic upgrade head`
6. `python -m main.py`
7. `celery -A tasks.transcribe_audio worker --loglevel=info`
8. `localhost:8000/docs`

### Running as docker-compose 
1. in `settings.toml` replace empty values in the [default] section with your variables
2. `docker-compose up --build`
3. `localhost:8000/docs`


## 🚀 Future Improvements

- **Tests!!!**
- **Speaker Recognition** — Not just what was said, but *who* said it
- **Multilanguage Support**
- **Switch to Whisper** — Test Whisper for file-based transcription, compare results
- **Fine-tuned Summarization Agent** — Current summary is generated via a LangGraph agent using a single tool. Improvements can include:
  - Action/Topic/Tag Extraction
  - Multilanguage Support via LangChain tools
- **WebRTC Support** — Enable in-browser audio capture for a smoother real-time experience
"""
- **GPU Acceleration** — Evaluate performance vs. cost
- **Explore Alternatives** — Investigate other open-source solutions for real-time speech recognition
- **Vosk Enhancements** — Improve text output with configs (inspired by [nerd-dictation](https://github.com/ideasman42/nerd-dictation))
- **Chunked Processing** — Break audio into chunks using Celery tasks
- **Refresh Token Handling**
- **User Management** — Roles, permissions, and beyond
- **Realtime Audio Save** — Continuous S3 upload of live speech
- **User-Specific Recognition** — Save users and identify them in audio files (Closed-system, lots of work)

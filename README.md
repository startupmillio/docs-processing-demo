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

# 🎙️ Intelligent Call Centre Analytic System

> An AI-powered API that processes Hinglish/Tanglish call centre audio and evaluates agent SOP compliance in real-time — built for GUVI Track 3.

[![Live API](https://img.shields.io/badge/Live%20API-Render-46E3B7?style=for-the-badge&logo=render)](https://intelligent-call-centre.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker)](https://docker.com)

---

## 🌐 Live Endpoint

```
POST https://intelligent-call-centre.onrender.com/api/call-analytics
```

> **Note:** Free tier may take ~50s on first request (cold start). Subsequent calls are fast.

---

## 🧠 How It Works

```
Client (Base64 MP3) 
    ↓  POST /api/call-analytics
FastAPI (auth via x-api-key)
    ↓
Celery Task Worker
    ↓
Gemini 2.5 Flash (native audio upload → simultaneous STT + NLP)
    ↓
Structured JSON Response
```

1. **API Reception** — Client sends a Base64-encoded `.mp3` via `POST /api/call-analytics`, authenticated by `x-api-key`.
2. **Background Processing** — The audio task is handed to **Celery**, backed by **Redis** as a message broker, keeping the API server non-blocking.
3. **Gemini Native Audio** — The audio file is uploaded directly to **Gemini 2.5 Flash**, which simultaneously transcribes Hinglish/Tanglish speech AND analyses the conversation — no separate STT library needed.
4. **SOP Validation** — Gemini evaluates the agent against a 5-step script: Greeting → Identification → Problem Statement → Solution → Closing.
5. **Structured Response** — A strict JSON schema is enforced, covering `transcript`, `summary`, `sop_validation`, `analytics`, and `keywords`.

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| API Framework | FastAPI + Uvicorn |
| Task Queue | Celery + Redis |
| AI / STT / NLP | Google Gemini 2.5 Flash |
| Containerisation | Docker + Docker Compose |
| Deployment | Render.com (Free tier) |

---

## 📁 Project Structure

```
.
├── app/
│   ├── main.py          # FastAPI endpoint + API key auth
│   ├── celery_app.py    # Celery worker configuration
│   ├── tasks.py         # Background task (audio → Gemini → JSON)
│   └── ml_services.py   # GeminiAudioService (STT + NLP in one call)
├── tests/
│   ├── test_api.py      # End-to-end API tester (local or production)
│   ├── test_audio.py    # Direct Gemini audio upload test
│   └── mock_test.py     # NLP-only test with hardcoded transcript
├── .env.example         # Environment variable template
├── Dockerfile           # Python 3.10 slim image
├── docker-compose.yml   # Multi-service orchestration
└── requirements.txt     # Python dependencies
```

---

## 🚀 Setup & Run

### Prerequisites
- Docker & Docker Compose installed
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)

### 1. Clone & Configure

```bash
git clone https://github.com/yash-goyal-0910/Intelligent-Call-Centre-Analytic-System.git
cd Intelligent-Call-Centre-Analytic-System

# Copy the example env file and fill in your API key
cp .env.example .env
```

Edit `.env`:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 2. Run with Docker

```bash
docker compose up --build -d
```

The API is now live at **`http://localhost:8000`**

### 3. Test the API

```bash
python tests/test_api.py sample.mp3 Tamil
```

To test the **live production URL**:
```bash
API_BASE_URL=https://intelligent-call-centre.onrender.com python tests/test_api.py sample.mp3 Tamil
```

---

## 📡 API Reference

### `POST /api/call-analytics`

**Headers:**
```
x-api-key: api_key_yash_0910
Content-Type: application/json
```

**Request Body:**
```json
{
  "language": "Tamil",
  "audioFormat": "mp3",
  "audioBase64": "<base64-encoded-mp3>"
}
```

**Response:**
```json
{
  "status": "success",
  "language": "Tamil",
  "transcript": "Agent: Vanakkam, TechConnect calling...\nCustomer: Haan, bolo...",
  "summary": "Agent called about outstanding EMI of ₹5000. Customer agreed to partial payment.",
  "sop_validation": {
    "greeting": true,
    "identification": true,
    "problemStatement": true,
    "solutionOffering": true,
    "closing": true,
    "complianceScore": 1.0,
    "adherenceStatus": "FOLLOWED",
    "explanation": "Agent followed all 5 SOP steps correctly."
  },
  "analytics": {
    "paymentPreference": "PARTIAL_PAYMENT",
    "rejectionReason": "BUDGET_CONSTRAINTS",
    "sentiment": "Neutral"
  },
  "keywords": ["EMI", "outstanding amount", "partial payment", "budget"]
}
```

### Allowed Enum Values

| Field | Values |
|-------|--------|
| `paymentPreference` | `EMI` · `FULL_PAYMENT` · `PARTIAL_PAYMENT` · `DOWN_PAYMENT` |
| `rejectionReason` | `HIGH_INTEREST` · `BUDGET_CONSTRAINTS` · `ALREADY_PAID` · `NOT_INTERESTED` · `NONE` |
| `adherenceStatus` | `FOLLOWED` · `NOT_FOLLOWED` |

---

## 🧪 Running Tests

| Test | Command | Requires |
|------|---------|----------|
| NLP-only (no server) | `python tests/mock_test.py` | `.env` with API key |
| Direct Gemini audio | `python tests/test_audio.py` | `.env` + `sample.mp3` |
| Full API (local) | `python tests/test_api.py sample.mp3 Tamil` | Docker running |
| Full API (production) | `API_BASE_URL=https://intelligent-call-centre.onrender.com python tests/test_api.py sample.mp3 Tamil` | Internet |

---

## ☁️ Deployment (Render.com)

1. Push to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com) → **New Web Service** → **GitHub repo**
3. Runtime: **Docker** (auto-detected from Dockerfile)
4. Add environment variables:
   - `GOOGLE_API_KEY` = your Gemini key
   - `API_KEY` = `api_key_yash_0910`
5. Deploy — Render builds the Docker image and goes live automatically

---

## 📋 Approach & Design Decisions

- **Gemini native audio** instead of `faster-whisper`: Gemini 2.5 Flash handles Hinglish/Tanglish transcription natively and with far higher accuracy than CPU-quantized Whisper models. This also eliminates heavy C/C++ build dependencies.
- **Single-pass architecture**: One Gemini call simultaneously transcribes and analyses — reducing latency and API round-trips.
- **Strict JSON schema**: The Gemini prompt enforces exact field names and enum values so evaluation responses never deviate from the required format.
- **Docker Compose**: Three-service stack (web + celery_worker + redis) ensures the system is fully reproducible across environments.

---

## 🤖 AI Tools Used

> **Disclosure:** The following AI tools were used in the development of this project, in compliance with the GUVI Track 3 AI Tool Policy.

| Tool | Provider | Purpose |
|------|----------|---------|
| **Google Gemini 2.5 Flash** | Google DeepMind | Core AI engine — native audio transcription (STT) and NLP analysis (SOP validation, analytics, keywords) in a single API call |
| **Google AI Studio** | Google | Gemini API key generation and prompt prototyping during development |
| **Antigravity (AI Coding Assistant)** | Google DeepMind | Pair-programming assistant used for architecture design, code generation, debugging, containerisation, and documentation |

### Gemini 2.5 Flash — Key Details
- **Model ID:** `gemini-2.5-flash`
- **SDK:** `google-genai==0.3.0`
- **Capabilities used:** Native audio file upload → simultaneous Speech-to-Text + NLP in one `generate_content()` call
- **Why Gemini over Whisper:** Handles Hinglish/Tanglish natively with no CPU-heavy C++ dependencies; eliminates a separate STT stage entirely

> A detailed AI Tools documentation PDF (`AI_Tools_Documentation.pdf`) is included in this repository.

---

## ⚠️ Known Limitations

| Limitation | Detail |
|-----------|--------|
| **Cold start latency** | Render.com free tier hibernates after inactivity — first request after idle can take ~50 seconds |
| **Synchronous polling** | The `/api/call-analytics` endpoint polls the Celery task result in a loop (up to 120 s). A WebSocket or callback-based approach would be more scalable |
| **No persistent storage** | Task results are stored in Redis only; restarting the Redis container clears all historical results |
| **Single API key auth** | Authentication uses a single static `x-api-key`; no per-user key management or rate limiting |
| **Free-tier resource ceiling** | Render free tier limits RAM; very long audio files (>10 min) may cause OOM errors in the Celery worker |

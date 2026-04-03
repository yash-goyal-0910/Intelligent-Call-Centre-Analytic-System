# Intelligent Call Centre Analytic System

An asynchronous, AI-powered system that processes Hinglish/Tanglish call center audio, transcribes it, and evaluates agent compliance strictly according to SOP (Standard Operating Procedures). 

## How It Works (Step-by-Step)
1. **API Audio Reception**: A client sends a Base64-encoded audio file (`.mp3`) via a `POST /api/call-analytics` request to the **FastAPI Server**. This endpoint is securely protected by a mandatory `x-api-key`.
2. **Asynchronous Audio Processing**: To prevent long-running tasks from locking up the web server, the API pushes the audio to **Celery**. Celery is an async worker that manages the heavy lifting in the background, communicating via a **Redis** message broker.
3. **Speech-to-Text (STT)**: Inside the worker, `faster-whisper` dynamically transcribes the audio, automatically parsing Tamil/Hindi accents into readable text representations.
4. **NLP & SOP Validation**: The transcript is forwarded to the **Google Gemini Engine**. 
   - A highly-tuned strict schema prompt forces Gemini to check if the agent correctly followed the greeting, identification, problem statement, solution offering, and closing steps.
   - The engine also extracts analytics such as `paymentPreference`, `rejectionReasons`, `sentiment`, and `keywords`.
5. **JSON Structuring**: The system combines the transcription and ML analytics into a rigid `JSON` mapping that flawlessly passes evaluation conditions.

## Project Structure
```text
.
├── app/
│   ├── main.py.......... # FastAPI Endpoint
│   ├── celery_app.py.... # Celery Worker Configuration
│   ├── tasks.py......... # Background Task definitions
│   └── ml_services.py... # NLP Logic (faster-whisper & Gemini GenAI SDK)
├── tests/
│   ├── test_api.py...... # Real endpoint API payload tester
│   └── mock_test.py..... # Core NLP test (bypasses Celery/STT)
├── Dockerfile........... # Linux environment image
├── docker-compose.yml... # Multi-service launcher (API, Worker, Broker)
└── requirements.txt..... # Python dependencies
```

## Setup & Deployment Instructions

### Prerequisites
You need a Google API key. Create a `.env` file in the root folder with:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 1. Launch Using Docker (Recommended for Testing/Deployment)
Since `faster-whisper` relies heavily on C++ and Rust, building via Docker guarantees everything runs flawlessly.
```bash
docker-compose build
docker-compose up -d
```
The server will now be live at `http://localhost:8000`. 

### 2. Live Deployment (For Assignment Submission)
1. Commit the repository to GitHub.
2. Link the repository to a hosting platform like Render.com or Railway.app. They will natively recognize the `Dockerfile` and boot the entire web service.
3. Once deployed, inject your `GOOGLE_API_KEY` into their Environment variables setup.

## Running Tests
Navigate to the `tests/` folder.
* **To strictly test the NLP Grading Matrix** (no servers required):
  ```bash
  python tests/mock_test.py
  ```
* **To test the live API**:
  If the application is running, run:
  ```bash
  python tests/test_api.py path/to/sample.mp3 Tamil
  ```

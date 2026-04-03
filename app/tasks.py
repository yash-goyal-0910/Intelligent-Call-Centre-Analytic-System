from app.celery_app import celery_app
from app.ml_services import GeminiAudioService
import base64
import tempfile
import traceback
import os

@celery_app.task(bind=True, name="process_audio_task")
def process_audio_task(self, language: str, audio_format: str, audio_base64: str):
    temp_file = None
    try:
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_base64)

        # Determine file extension
        ext = ".mp3" if audio_format.lower() == "mp3" else f".{audio_format.lower()}"

        # Write to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        temp_file.write(audio_bytes)
        temp_file.flush()
        audio_path = temp_file.name
        temp_file.close()

        # Single Gemini call: STT + NLP analysis together
        service = GeminiAudioService()
        result = service.process_audio(audio_path, language)

        # Build final response matching the required schema
        response = {
            "status": "success",
            "language": language,
            **result,  # includes transcript, summary, sop_validation, analytics, keywords
        }

        return response

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file.name):
            os.remove(temp_file.name)

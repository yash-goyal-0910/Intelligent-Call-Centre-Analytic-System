import os
import json
from google import genai

PROMPT_TEMPLATE = """
You are an expert Call Center Quality Analyst. Listen to this audio recording of a customer service call in Hinglish or Tanglish (a mix of Tamil/Hindi and English). 

First, transcribe the full audio internally, then analyze it using these rules:

1. **Transcript**: Provide the full verbatim transcription of the spoken audio in readable English/Hinglish/Tanglish. Label each line as "Agent:" or "Customer:" where possible.
2. **Summary**: A concise summary of the conversation.
3. **SOP Validation**: The standard script is Greeting → Identification → Problem Statement → Solution Discussion → Closing.
   - For each step, it's true if performed by the agent, false otherwise.
   - Score compliance (0.0 to 1.0).
   - Adherence status MUST be exactly "FOLLOWED" or "NOT_FOLLOWED".
4. **Analytics**:
   - paymentPreference MUST strictly map to one of: EMI, FULL_PAYMENT, PARTIAL_PAYMENT, or DOWN_PAYMENT.
   - If a sale is not closed / payment not made, rejectionReason MUST be one of: HIGH_INTEREST, BUDGET_CONSTRAINTS, ALREADY_PAID, NOT_INTERESTED, or NONE.
   - sentiment (e.g. "Neutral", "Positive", "Negative").
5. **Keywords**: A list of the main keywords/topics discussed.

Return the result as STRICT, VALID JSON formatted EXACTLY like this with no trailing commas, markdown blocks, formatting or extra text:
{{
  "transcript": "[Full spoken transcript of the audio]",
  "summary": "...",
  "sop_validation": {{
    "greeting": true,
    "identification": false,
    "problemStatement": true,
    "solutionOffering": true,
    "closing": true,
    "complianceScore": 0.8,
    "adherenceStatus": "FOLLOWED",
    "explanation": "..."
  }},
  "analytics": {{
    "paymentPreference": "PARTIAL_PAYMENT",
    "rejectionReason": "BUDGET_CONSTRAINTS",
    "sentiment": "Neutral"
  }},
  "keywords": ["...", "..."]
}}
"""


def _parse_gemini_json(text: str) -> dict:
    """Strip markdown fences and parse JSON from Gemini's response."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini failed to produce valid JSON. Error: {e}\nRaw output:\n{text}")


class GeminiAudioService:
    """
    Single-step service: uploads the audio file directly to Gemini and asks it to 
    simultaneously transcribe (STT) and analyse (NLP) the call in one API call.
    This approach handles Tanglish/Hinglish far better than faster-whisper on CPU.
    """

    def __init__(self):
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is missing.")
        self.client = genai.Client()

    def process_audio(self, audio_path: str, language: str) -> dict:
        """Upload audio to Gemini and get transcript + NLP analysis back as a dict."""
        audio_file = self.client.files.upload(path=audio_path)
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[audio_file, PROMPT_TEMPLATE],
        )
        return _parse_gemini_json(response.text)


# ---------------------------------------------------------------------------
# Kept for backwards-compatibility / fallback (not used in main pipeline)
# ---------------------------------------------------------------------------
class LLMService:
    """Analyses a pre-existing transcript string with Gemini (text-only path)."""

    def __init__(self):
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is missing.")
        self.client = genai.Client()

    def analyze_transcript(self, transcript: str) -> dict:
        prompt = f"""
        You are an expert Call Center Quality Analyst. Read the following transcript and extract the requested fields.

        TRANSCRIPT:
        '''
        {transcript}
        '''

        Analyze it using these rules:
        1. **Summary**: A concise summary of the conversation.
        2. **SOP Validation**: The standard script is Greeting → Identification → Problem Statement → Solution Discussion → Closing.
           - For each step, it's true if performed by the agent, false otherwise.
           - Score compliance (0.0 to 1.0).
           - Adherence status MUST be exactly "FOLLOWED" or "NOT_FOLLOWED".
        3. **Analytics**:
           - paymentPreference MUST strictly map to one of: EMI, FULL_PAYMENT, PARTIAL_PAYMENT, or DOWN_PAYMENT.
           - If a sale is not closed / payment not made, rejectionReason MUST be one of: HIGH_INTEREST, BUDGET_CONSTRAINTS, ALREADY_PAID, NOT_INTERESTED, or NONE.
           - sentiment (e.g. "Neutral", "Positive", "Negative").
        4. **Keywords**: A list of the main keywords/topics discussed.

        Return the result as STRICT, VALID JSON formatted EXACTLY like this with no trailing commas, markdown blocks, formatting or extra text:
        {{
          "summary": "...",
          "sop_validation": {{
            "greeting": true,
            "identification": false,
            "problemStatement": true,
            "solutionOffering": true,
            "closing": true,
            "complianceScore": 0.8,
            "adherenceStatus": "FOLLOWED",
            "explanation": "..."
          }},
          "analytics": {{
            "paymentPreference": "PARTIAL_PAYMENT",
            "rejectionReason": "BUDGET_CONSTRAINTS",
            "sentiment": "Neutral"
          }},
          "keywords": ["...", "..."]
        }}
        """
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return _parse_gemini_json(response.text)

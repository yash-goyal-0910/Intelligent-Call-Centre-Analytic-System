import os
import json
from google import genai

# Load API key
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('GOOGLE_API_KEY='):
            os.environ['GOOGLE_API_KEY'] = line.strip().split('=')[1]

client = genai.Client()

def test_audio(path):
    print(f"Uploading {path} to Gemini for Audio Processing...")
    
    # Upload the audio file directly using the new SDK!
    audio_file = client.files.upload(file=path)
    
    print("Upload complete. Running STT Transcription AND NLP Scoring natively...")
    
    prompt = f"""
    You are an expert Call Center Quality Analyst. Listen to this audio recording of a customer service call. 
    First, transcribe it internally, then analyze it using these rules:
    
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
      "transcript": "[Insert the full spoken transcript of the audio in English/Hinglish/Tanglish]",
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
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[audio_file, prompt]
    )
    
    text = response.text.strip()
    if text.startswith("```json"): text = text[7:]
    if text.startswith("```"): text = text[3:]
    if text.endswith("```"): text = text[:-3]
    
    try:
        parsed = json.loads(text.strip())
        print("====== GENAI AUDIO -> JSON OUTPUT ======")
        print(json.dumps(parsed, indent=2))
        print("========================================")
        print("Success! Gemini natively transcribed and scored the audio successfully.")
    except Exception as e:
        print("Failed to parse JSON:", str(e))
        print("Raw output:", text)

if __name__ == "__main__":
    if os.path.exists("sample.mp3"):
        test_audio("sample.mp3")
    else:
        print("sample.mp3 not found!")

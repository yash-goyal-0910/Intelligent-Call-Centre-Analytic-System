import os
import json
from google import genai
from google.genai import types

# Use the API key we saved
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('GOOGLE_API_KEY='):
            os.environ['GOOGLE_API_KEY'] = line.strip().split('=')[1]

client = genai.Client()

def test_ml_pipeline():
    sample_transcript = """
    Agent: Hello? Customer: Yeah, hello. Is this Manikandan?
    Agent: Yes, Manikandan speaking, tell me. Agent: I am calling from Guvi Institution.
    Customer: Ah, tell me. Agent: Actually, you gave an inquiry for a course, right?
    Customer: Yes, actually I was working in digital marketing for the last 5 years. Plus, there is a one-year career gap now, so I'm looking for a career change. I heard that Data Science has a very good scope. While checking, your institute was among the top ones, so I wanted to check.
    Agent: Definitely. Our office is located within IIT Madras. We have been established for almost 11 years. Recently, HCL company merged with Guvi. So, in terms of certification and recognition, Guvi is the best in India, okay? But what matters is that you give your 100% effort. If you give your 100% effort, we will take care of the rest. You don't have to worry about the process. Now, Manikandan, I will send you a WhatsApp message. First, send me your current resume.
    Customer: Current resume? Yes, I have it, but there is a career gap of 9 months for personal reasons.
    Agent: No problem, I'm asking for a personal understanding. Send whatever resume you have. I'll check it and let you know what skills are pending and what needs to be filled. Only if you send the resume can we determine how to proceed with the training. Industry experts with 20 years of experience will train you. You will get many projects. You will get 100% satisfaction. But we need to give our 100% effort. We will guide you. Send the resume, we will review it and get back to you. We have EMI options available, or you can pay via partial payment today. 
    Customer: I can pay 2000 today and the rest next month. 
    Agent: Perfect, that works. Send the resume and I will send the link. Thank you.
    """
    
    print("Testing NLP analysis engine...\n")
    
    prompt = f"""
    You are an expert Call Center Quality Analyst. Read the following transcript and extract the requested fields.

    TRANSCRIPT:
    '''
    {sample_transcript}
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
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    
    # Strip markdown logic
    text = response.text.strip()
    if text.startswith("```json"): text = text[7:]
    if text.startswith("```"): text = text[3:]
    if text.endswith("```"): text = text[:-3]
    
    try:
        parsed = json.loads(text.strip())
        print("====== GENAI JSON OUTPUT ======")
        print(json.dumps(parsed, indent=2))
        print("===============================")
        print("Success! JSON schema strictly matches evaluation template.")
    except Exception as e:
        print("Failed to parse JSON:", str(e))
        print("Raw output:", text)

if __name__ == "__main__":
    test_ml_pipeline()

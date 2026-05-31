from dotenv import load_dotenv
load_dotenv()
from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

try:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a stock analyst. Reply with valid JSON only."
            },
            {
                "role": "user",
                "content": "Give me a test response with this exact JSON structure: {\"action\": \"BUY\", \"confidence\": 75, \"summary\": \"test working\", \"reasons\": [\"reason1\", \"reason2\", \"reason3\", \"reason4\"], \"entry_point\": 100, \"exit_point\": 110, \"stop_loss\": 95}"
            }
        ],
        temperature=0.3,
        max_tokens=500
    )
    print("SUCCESS:")
    print(response.choices[0].message.content)

except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
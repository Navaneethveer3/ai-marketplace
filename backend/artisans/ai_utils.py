import os

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# Only import OpenAI if key exists
if OPENAI_KEY:
    import openai
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_KEY)

    def generate_ai_text(prompt: str, max_tokens: int = 60) -> str:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a creative assistant for artisans and handcrafted products."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[AI error: {str(e)}]"
else:
    # Mock function if no API key
    def generate_ai_text(prompt: str, max_tokens: int = 60) -> str:
        return "[AI functionality disabled in production]"

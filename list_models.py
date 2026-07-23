from google import genai

API_KEY = "PASTE_YOUR_GEMINI_API_KEY"

client = genai.Client(api_key=API_KEY)

for model in client.models.list():
    print(model.name)
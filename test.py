from google import genai

client = genai.Client(api_key="PASTE_YOUR_API_KEY")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say Hello"
)

print(response.text)
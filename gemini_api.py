from google import genai

client = genai.Client(api_key="AIzaSyCHJhOsy12cREX8KNdCOAxrMw_L8cqQlK0")

response = client.models.generate_content(
    model="gemini-2.0-flash-lite", contents="Explain how AI works in a few words"
)
print(response.text)
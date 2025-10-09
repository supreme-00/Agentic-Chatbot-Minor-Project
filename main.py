from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="AIzaSyC-F2qRBSbOIaLaOfJsL39j2SPJBjNSIIc")

# List available models (optional, for verification)
for m in genai.list_models():
    print(m.name, m.supported_generation_methods)

# Use a current supported model
model = genai.GenerativeModel("models/gemini-1.5-flash")

app = FastAPI()

# Allow frontend (HTML/JS) to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "FastAPI Gemini Chatbot is running!"}


# ✅ Check if query is related to Ganpat University
def is_ganpat_related(query: str) -> bool:
    keywords = [
        "ganpat", "uvpce", "guni", "campus", "admission", "faculty",
        "placement", "hostel", "canteen", "library", "engineering", "pharmacy"
    ]
    return any(kw in query.lower() for kw in keywords)


@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message")

    # ✅ Add system instructions depending on context
    if is_ganpat_related(user_message):
        system_instruction = """
        You are Ganpat University’s official campus chatbot.
        Always provide helpful, accurate information about Ganpat University, 
        UVPCE, faculties, admissions, placements, hostels, campus life, and events.
        Do not include irrelevant information.
        """
    else:
        system_instruction = """
        You are Ganpat University’s chatbot.
        Prefer answering questions about Ganpat University (courses, faculty, events, placements, etc.).
        If a question is unrelated, answer politely in 1-2 lines.
        You may answer general factual questions if possible, then gently guide the user back to campus topics.

        """

    # Send both system instruction and user message to Gemini
    response = model.generate_content([system_instruction, user_message])
    reply = response.text

    return {"reply": reply}

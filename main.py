from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/feedback")
async def get_feedback(
    text: str = Form(...),
    language: str = Form(...)
):
    if not openai.api_key:
        return JSONResponse(content={"error": "Missing OpenAI API key"}, status_code=500)

    if language == "en":
        prompt = f"""
You are a Spanish teacher. A student wrote the following text in Spanish:
{text}

Give friendly and clear feedback in English as if you were their personal tutor.
- Correct grammar or usage mistakes (if any)
- Suggest improvements
- Be supportive

Use clear formatting like:
✅ Correct
✍️ Suggested correction
💡 Tips
"""
    else:
        prompt = f"""
Eres profesor de español. Un estudiante escribió este texto:
{text}

Dale un feedback claro y amable en español como si fueras su tutor personal.
- Corrige errores gramaticales o de uso si los hay
- Sugiere mejoras
- Sé positivo y cercano

Usa un formato como:
✅ Correcto
✍️ Corrección sugerida
💡 Consejos
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=500
        )
        feedback = response.choices[0].message.content.strip()
        return JSONResponse(content={"feedback": feedback})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

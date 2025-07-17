@@ -1,64 +1,73 @@
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fpdf import FPDF
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/feedback", response_class=HTMLResponse)
async def feedback(
    request: Request,
    student_name: str = Form(...),
    exercise_title: str = Form(...),
    language: str = Form(...),
    student_text: str = Form(...)
@app.post("/feedback")
async def get_feedback(
    text: str = Form(...),
    language: str = Form(...)
):
    prompt = f"Corrige el siguiente texto en {language}. Incluye sugerencias útiles y explica brevemente los errores si existen:\n\n{student_text}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    feedback_text = response.choices[0].message.content
    return templates.TemplateResponse("index.html", {
        "request": request,
        "student_name": student_name,
        "exercise_title": exercise_title,
        "student_text": student_text,
        "feedback_text": feedback_text,
        "language": language
    })
    if not openai.api_key:
        return JSONResponse(content={"error": "Missing OpenAI API key"}, status_code=500)

@app.post("/generate_pdf")
async def generate_pdf(
    student_name: str = Form(...),
    exercise_title: str = Form(...),
    student_text: str = Form(...),
    feedback_text: str = Form(...)
):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
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

    pdf.cell(200, 10, txt=f"Nombre: {student_name}", ln=True)
    pdf.cell(200, 10, txt=f"Ejercicio: {exercise_title}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt="Texto del estudiante:\n" + student_text)
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt="Feedback del profesor:\n" + feedback_text)
Dale un feedback claro y amable en español como si fueras su tutor personal.
- Corrige errores gramaticales o de uso si los hay
- Sugiere mejoras
- Sé positivo y cercano

    pdf_path = f"/mnt/data/{student_name}_{exercise_title}.pdf"
    pdf.output(pdf_path)
Usa un formato como:
✅ Correcto
✍️ Corrección sugerida
💡 Consejos
"""

    return FileResponse(pdf_path, media_type='application/pdf', filename=os.path.basename(pdf_path))
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

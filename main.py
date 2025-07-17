from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fpdf import FPDF
import openai
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/feedback", response_class=HTMLResponse)
async def feedback(
    request: Request,
    student_name: str = Form(...),
    exercise_title: str = Form(...),
    language: str = Form(...),
    student_text: str = Form(...)
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

    pdf.cell(200, 10, txt=f"Nombre: {student_name}", ln=True)
    pdf.cell(200, 10, txt=f"Ejercicio: {exercise_title}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt="Texto del estudiante:\n" + student_text)
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt="Feedback del profesor:\n" + feedback_text)

    pdf_path = f"/mnt/data/{student_name}_{exercise_title}.pdf"
    pdf.output(pdf_path)

    return FileResponse(pdf_path, media_type='application/pdf', filename=os.path.basename(pdf_path))
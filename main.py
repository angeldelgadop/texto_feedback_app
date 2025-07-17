import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from openai import OpenAI
from fpdf import FPDF

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Ruta inicial
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Ruta para procesar el feedback
@app.post("/feedback", response_class=HTMLResponse)
async def feedback(
    request: Request,
    student_name: str = Form(...),
    exercise_title: str = Form(...),
    student_text: str = Form(...),
    language: str = Form(...)
):
    prompt = f"""Eres un profesor de español. Revisa el siguiente texto del estudiante y ofrece correcciones y sugerencias claras.

Texto del estudiante:
{student_text}

Idioma del feedback: {language}
"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        feedback_text = response.choices[0].message.content
    except:
        feedback_text = "No se pudo generar el feedback."

    return templates.TemplateResponse("index.html", {
        "request": request,
        "student_name": student_name,
        "exercise_title": exercise_title,
        "student_text": student_text,
        "feedback_text": feedback_text
    })

# Ruta para generar el PDF
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

    pdf.cell(200, 10, txt="Texto Chévere - Feedback del Estudiante", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Nombre: {student_name}", ln=True)
    pdf.cell(200, 10, txt=f"Título del ejercicio: {exercise_title}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt="Texto del estudiante:")
    pdf.multi_cell(0, 10, txt=student_text)
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt="Feedback del profesor:")
    pdf.multi_cell(0, 10, txt=feedback_text)

    output_path = f"/tmp/{student_name}_{exercise_title}.pdf"
    pdf.output(output_path)

    from fastapi.responses import FileResponse
    return FileResponse(path=output_path, filename="feedback.pdf", media_type="application/pdf")

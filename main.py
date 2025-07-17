from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from openai import OpenAI
from io import BytesIO
from fpdf import FPDF
import os
import dotenv

dotenv.load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def form_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/feedback", response_class=HTMLResponse)
async def get_feedback(
    request: Request,
    student_name: str = Form(...),
    exercise_title: str = Form(...),
    student_text: str = Form(...),
    language: str = Form(...)
):
    prompt = f"Eres un profesor de español. Revisa el siguiente texto del estudiante y ofrece correcciones y sugerencias claras. El texto es:

{student_text}"
    if language == "inglés":
        prompt = f"You are a Spanish teacher. Review the student's text below and give clear corrections and suggestions in English. The text is:

{student_text}"

    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful and friendly Spanish teacher."},
            {"role": "user", "content": prompt}
        ]
    )

    feedback_text = completion.choices[0].message.content.strip()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "student_name": student_name,
        "exercise_title": exercise_title,
        "student_text": student_text,
        "language": language,
        "feedback_text": feedback_text
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
    pdf.cell(200, 10, txt="Texto Chévere - Feedback del Profesor", ln=True, align="C")
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=f"👤 Nombre: {student_name}")
    pdf.multi_cell(0, 10, txt=f"📝 Título del ejercicio: {exercise_title}")
    pdf.ln(5)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0, 10, txt="Texto del estudiante:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=student_text)
    pdf.ln(5)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0, 10, txt="Feedback del profesor:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=feedback_text)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return StreamingResponse(pdf_output, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=feedback_{student_name.replace(' ', '_')}.pdf"
    })

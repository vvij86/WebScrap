from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import openai
import pandas as pd
import fitz  # PyMuPDF
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define Pydantic model for questions
class Questions(BaseModel):
    questions: List[str]

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file: UploadFile) -> str:
    try:
        pdf_reader = fitz.open(stream=pdf_file.file.read(), filetype="pdf")
        text = ""
        for page_num in range(len(pdf_reader)):
            page = pdf_reader.load_page(page_num)
            text += page.get_text()
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading PDF file: {e}")

# Function to get answer from GPT-4
def get_answer_from_gpt4(question: str, context: str) -> str:
    try:
        prompt = f"Context: {context}\n\nQuestion: {question}\nAnswer:"
        response = openai.Completion.create(
            model="gpt-4",
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {e}")

# Endpoint to process PDF and questions
@app.post("/process-pdf/")
async def process_pdf(
    file: UploadFile = File(...),
    questions: str = Form(...)
):
    # Extract text from PDF
    pdf_text = extract_text_from_pdf(file)

    # Parse questions
    questions_list = questions.split("\n")

    # Generate answers
    answers = [get_answer_from_gpt4(question, pdf_text) for question in questions_list]

    # Create a DataFrame
    df = pd.DataFrame([answers], columns=questions_list)

    # Save to Excel
    output_file = "output.xlsx"
    df.to_excel(output_file, index=False)

    return FileResponse(output_file, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=output_file)

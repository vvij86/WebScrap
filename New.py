from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import pandas as pd
import fitz  # PyMuPDF
import os
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

load_dotenv()

app = FastAPI()

# Pydantic response model
class Answer(BaseModel):
    question: str = Field(description="The question asked.")
    answer: str = Field(description="Answer from the PDF content.")

# Azure OpenAI setup using environment variables
provider = OpenAIProvider(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2024-02-01"
)

openai_model = OpenAIModel(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    provider=provider
)

# Initialize the PydanticAI Agent
agent = Agent(
    model=openai_model,
    system_prompt="You are an expert assistant that answers questions based on provided context.",
    result_type=Answer
)

# Extract text from PDF
def extract_text_from_pdf(pdf_file: UploadFile) -> str:
    try:
        pdf_reader = fitz.open(stream=pdf_file.file.read(), filetype="pdf")
        return ''.join(page.get_text() for page in pdf_reader)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading PDF file: {e}")

# Get answer using the agent
async def get_answer(question: str, context: str) -> str:
    prompt = f"Context:\n{context}\n\nQuestion:\n{question}\n\nProvide a concise answer based on the context."
    result = await agent.run(prompt)
    return result.data.answer

# Endpoint to process PDF and questions
@app.post("/process-pdf/")
async def process_pdf(file: UploadFile = File(...), questions: str = Form(...)):
    pdf_text = extract_text_from_pdf(file)
    questions_list = [q.strip() for q in questions.strip().split("\n") if q.strip()]

    answers = []
    for question in questions_list:
        answer = await get_answer(question, pdf_text)
        answers.append(answer)

    df = pd.DataFrame([answers], columns=questions_list)
    output_file = "output.xlsx"
    df.to_excel(output_file, index=False)

    return FileResponse(
        output_file,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename=output_file
    )

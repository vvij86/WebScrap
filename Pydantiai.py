from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List
import pandas as pd
import fitz  # PyMuPDF
import os
from dotenv import load_dotenv
import openai
from pydantic_ai import Agent, OpenAIModel

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Set OpenAI API key and endpoint from environment variables
openai.api_type = "azure"
openai.api_key = os.getenv('AZURE_OPENAI_API_KEY')
openai.api_base = os.getenv('AZURE_OPENAI_ENDPOINT')
openai.api_version = "2024-08-01-preview"  # Use the appropriate API version

# Define Pydantic model for structured response
class Answer(BaseModel):
    question: str = Field(description="The question posed")
    answer: str = Field(description="The answer to the question")

# Custom OpenAI client for Azure
class AzureOpenAIClient:
    def __init__(self, deployment_name: str):
        self.deployment_name = deployment_name

    def create_completion(self, prompt: str, **kwargs):
        response = openai.Completion.create(
            engine=self.deployment_name,
            prompt=prompt,
            **kwargs
        )
        return response

# Initialize PydanticAI Agent with custom OpenAI client
azure_openai_client = AzureOpenAIClient(deployment_name=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'))
agent = Agent(
    model=OpenAIModel(client=azure_openai_client),
    system_prompt='You are an assistant extracting information from a PDF document to answer specific questions.',
    result_type=Answer,
)

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

# Function to get answer from PydanticAI Agent
async def get_answer_from_agent(question: str, context: str) -> str:
    try:
        result = await agent.run(question, context=context)
        return result.data.answer
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
    answers = [await get_answer_from_agent(question, pdf_text) for question in questions_list]

    # Create a DataFrame
    df = pd.DataFrame([answers], columns=questions_list)

    # Save to Excel
    output_file = "output.xlsx"
    df.to_excel(output_file, index=False)

    return FileResponse(output_file, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=output_file)

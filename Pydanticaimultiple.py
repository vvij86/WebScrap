import os
import fitz  # PyMuPDF
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import ElasticsearchStore
from langchain.chat_models import AzureChatOpenAI
from langchain.chains import RetrievalQA
from pydantic_ai import Agent
from pydantic import BaseModel, Field
import pandas as pd
from typing import List

# Extract PDF text
def extract_text_from_pdfs(directory: str) -> dict:
    pdf_texts = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                file_path = os.path.join(root, file)
                doc = fitz.open(file_path)
                text = ''
                for page in doc:
                    text += page.get_text()
                pdf_texts[file_path] = text
    return pdf_texts

# Initialize Elasticsearch vector store
def setup_vector_store(es_url: str, es_user: str, es_password: str, index_name: str):
    embeddings = OpenAIEmbeddings()
    vector_store = ElasticsearchStore(
        embedding=embeddings,
        index_name=index_name,
        es_url=es_url,
        es_user=es_user,
        es_password=es_password
    )
    return vector_store

# Load questions
def load_questions(filepath: str) -> List[str]:
    with open(filepath, 'r') as f:
        return [line.strip() for line in f if line.strip()]

# Pydantic-AI structured response
class QAResponse(BaseModel):
    responses: List[dict] = Field(description="List of question-answer pairs")

# Get answers using RetrievalQA chain
def get_answers(vector_store, llm, questions):
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

    prompt = "\n".join(f"Q: {q}" for q in questions)
    response = qa_chain.run(prompt)

    # Initialize pydantic-ai agent for structured parsing
    agent = Agent(model='openai:gpt-4', api_key='your_openai_api_key', result_type=QAResponse,
                  system_prompt="Extract questions and their corresponding answers clearly.")

    structured_response = agent.run_sync(response)
    return structured_response.data.responses

# Save to Excel
def save_to_excel(data, questions, output_file):
    df = pd.DataFrame(data)
    columns_order = ['file_path'] + questions
    df = df[columns_order]
    df.to_excel(output_file, index=False)

# Main Workflow
def main(pdf_directory, es_url, es_user, es_password, index_name, questions_file, deployment_name, openai_api_key, output_file):
    pdf_texts = extract_text_from_pdfs(pdf_directory)
    vector_store = setup_vector_store(es_url, es_user, es_password, index_name)

    # Add texts to vector store with metadata
    for path, text in pdf_texts.items():
        chunks = text.split('\n\n')
        metadatas = [{"file_path": path} for _ in chunks]
        vector_store.add_texts(chunks, metadatas=metadatas)

    llm = AzureChatOpenAI(deployment_name=deployment_name, openai_api_key=openai_api_key)

    questions = load_questions(questions_file)

    results = []
    for file_path in pdf_texts:
        filtered_vector_store = vector_store.as_retriever(search_kwargs={"k": 5, "filter": {"file_path": file_path}})
        qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=filtered_vector_store)

        prompt = "\n".join(f"Q: {q}" for q in questions)
        response = qa_chain.run(prompt)

        # Structure response using pydantic-ai
        agent = Agent(model='openai:gpt-4', api_key=openai_api_key, result_type=QAResponse,
                      system_prompt="Provide structured pairs of questions and answers.")
        structured_response = agent.run_sync(response)

        row = {"file_path": file_path}
        for qa_pair in structured_response.data.responses:
            row[qa_pair['question']] = qa_pair['answer']
        results.append(row)

    save_to_excel(results, questions, output_file)

if __name__ == "__main__":
    # Replace these parameters accordingly
    main(
        pdf_directory="path_to_your_pdf_directory",
        es_url="http://localhost:9200",
        es_user="elastic",
        es_password="your_es_password",
        index_name="pdf_embeddings",
        questions_file="questions.txt",
        deployment_name="your_azure_deployment_name",
        openai_api_key="your_openai_api_key",
        output_file="output.xlsx"
    )

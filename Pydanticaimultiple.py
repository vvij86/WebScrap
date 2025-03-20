import os
import fitz  # PyMuPDF
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import ElasticsearchStore
from pydantic import BaseModel, Field
from pydantic_ai import Agent
import pandas as pd
from typing import List

# Step 1: Extract text from PDFs using PyMuPDF
def extract_text_from_pdfs(directory: str) -> dict:
    pdf_texts = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                file_path = os.path.join(root, file)
                doc = fitz.open(file_path)
                text = ""
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text += page.get_text()
                pdf_texts[file_path] = text
    return pdf_texts

# Step 2: Initialize OpenAI embeddings and Elasticsearch vector store
def initialize_vector_store(es_url: str, es_user: str, es_password: str, index_name: str) -> ElasticsearchStore:
    embedding = OpenAIEmbeddings()
    vector_store = ElasticsearchStore(
        embedding=embedding,
        index_name=index_name,
        es_url=es_url,
        es_user=es_user,
        es_password=es_password
    )
    return vector_store

# Step 3: Process and store embeddings
def store_embeddings(vector_store: ElasticsearchStore, pdf_texts: dict):
    for file_path, text in pdf_texts.items():
        # Split text into manageable chunks
        chunks = text.split('\n\n')  # Adjust the splitting logic as needed
        # Create metadata with the file path
        metadatas = [{"file_path": file_path} for _ in chunks]
        # Add text chunks to the vector store
        vector_store.add_texts(chunks, metadatas=metadatas)

# Step 4: Load questions from a text file
def load_questions(questions_file: str) -> List[str]:
    with open(questions_file, 'r') as file:
        questions = [line.strip() for line in file if line.strip()]
    return questions

# Pydantic model for structured output
class QnA(BaseModel):
    question: str = Field(description="The question posed to the LLM")
    answer: str = Field(description="The LLM's response to the question")

# Step 5: Initialize the Pydantic-AI Agent
def initialize_llm_agent(model_name: str, api_key: str) -> Agent:
    return Agent(
        model=model_name,
        api_key=api_key,
        result_type=QnA,
        system_prompt='You are an AI assistant. Answer the following questions based on the provided text.'
    )

# Step 6: Query the LLM
def get_answers_from_llm(agent: Agent, text: str, questions: List[str]) -> List[QnA]:
    responses = []
    for question in questions:
        prompt = f"Based on the following text:\n\n{text}\n\nAnswer the question: {question}"
        result = agent.run_sync(prompt)
        responses.append(result.data)
    return responses

# Step 7: Retrieve relevant texts, generate answers, and save to Excel
def generate_answers_and_save_to_excel(vector_store: ElasticsearchStore, pdf_texts: dict, questions: List[str], agent: Agent, output_file: str):
    # Initialize a DataFrame to store the results
    df = pd.DataFrame(columns=['file_path'] + questions)

    for file_path in pdf_texts.keys():
        # Retrieve relevant text chunks
        relevant_docs = vector_store.similarity_search(query=" ".join(questions), k=5, filter={"file_path": file_path})
        combined_text = " ".join([doc.page_content for doc in relevant_docs])
        # Get answers from the LLM
        qna_pairs = get_answers_from_llm(agent, combined_text, questions)
        # Prepare the row for the DataFrame
        row = {'file_path': file_path}
        row.update({qna.question: qna.answer for qna in qna_pairs})
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    # Save the DataFrame to an Excel file
    df.to_excel(output_file, index=False)

# Main function to execute the workflow
def main(pdf_directory: str, es_url: str, es_user: str, es_password: str, index_name: str, questions_file: str, model_name: str, api_key: str, output_file: str):
    # Extract text from PDFs
    pdf_texts = extract_text_from_pdfs(pdf_directory)
    # Initialize vector store
    vector_store = initialize_vector_store(es_url, es_user, es_password, index_name)
    # Store embeddings
    store_embeddings(vector_store, pdf_texts)
    # Load questions
    questions = load_questions(questions_file)
    # Initialize LLM Agent
    llm_agent = initialize_llm_agent(model_name, api_key)
    # Generate answers and save to Excel
    generate_answers_and_save_to_excel(vector_store, pdf_texts, questions, llm_agent, output_file)

if __name__ == "__main__":
    # Define your parameters
    pdf_directory = 'path_to_your_pdf_directory'
    es_url = 'http://localhost:9200'  # Replace with your Elasticsearch URL
    es_user = 'elastic'               # Replace with your Elasticsearch username
    es_password = 'password'          # Replace with your Elasticsearch password
    index_name = 'pdf_embeddings'
    questions_file = 'questions.txt'
    model_name = 'openai:gpt-4'       # Replace with your desired OpenAI model
    api_key = 'your_api_key'          # Replace with your OpenAI API key
    output_file = 'output.xlsx'

    main(pdf_directory, es_url, es_user, es_password, index_name, questions_file, model_name, api_key, output_file)

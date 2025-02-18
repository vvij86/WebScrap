import os
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from scrapegraphai.graphs import SmartScraperGraph

def main():
    # Retrieve Azure OpenAI settings from environment variables or use defaults
    azure_api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2023-07-01-preview")
    azure_chat_deployment = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "o1-preview-deployment")
    azure_embeddings_deployment = os.environ.get("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME", "o1-preview-embeddings")

    # Initialize the Azure OpenAI LLM instance for chat completions
    lm_model_instance = AzureChatOpenAI(
        openai_api_version=azure_api_version,
        azure_deployment=azure_chat_deployment
    )

    # Initialize the Azure OpenAI embeddings model instance
    embedder_model_instance = AzureOpenAIEmbeddings(
        azure_deployment=azure_embeddings_deployment,
        openai_api_version=azure_api_version
    )

    # Configure the graph using the Azure model instances
    graph_config = {
        "llm": {"model_instance": lm_model_instance},
        "embeddings": {"model_instance": embedder_model_instance},
        "verbose": True,    # Optional: enables more detailed logging
        "headless": True    # Run headless to avoid opening a browser window
    }

    # Define your scraping prompt and source URL
    prompt = "Explain graph neural networks in simple terms. Provide a brief summary and key points."
    source_url = "https://example.com/articles-about-gnn"  # Update to a valid URL

    # Create an instance of SmartScraperGraph with the prompt, source, and config
    smart_scraper = SmartScraperGraph(
        prompt=prompt,
        source=source_url,
        config=graph_config
    )

    # Run the scraper graph to extract information
    result = smart_scraper.run()

    # Print the extracted result
    print("Scraping Result:")
    print(result)

if __name__ == "__main__":
    main()

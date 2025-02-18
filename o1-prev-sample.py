import os
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from scrapegraphai.graphs import SearchGraph

def main():
    # Retrieve Azure settings from environment variables or use defaults
    azure_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    if not azure_api_key:
        raise ValueError("Please set the AZURE_OPENAI_API_KEY environment variable.")
    
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "https://your-resource-name.openai.azure.com/")
    azure_api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2023-07-01-preview")
    azure_chat_deployment = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "o1-preview-deployment")
    azure_embeddings_deployment = os.environ.get("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME", "o1-preview-embeddings")

    # Initialize the Azure OpenAI LLM instance for chat completions
    lm_model_instance = AzureChatOpenAI(
        openai_api_key=azure_api_key,
        azure_endpoint=azure_endpoint,
        openai_api_version=azure_api_version,
        azure_deployment=azure_chat_deployment
    )

    # Initialize the Azure OpenAI embeddings model instance
    embedder_model_instance = AzureOpenAIEmbeddings(
        openai_api_key=azure_api_key,
        azure_endpoint=azure_endpoint,
        openai_api_version=azure_api_version,
        azure_deployment=azure_embeddings_deployment
    )

    # Configure the graph using the Azure model instances
    graph_config = {
        "llm": {"model_instance": lm_model_instance},
        "embeddings": {"model_instance": embedder_model_instance},
        "verbose": True,    # Enables detailed logging
        "headless": True    # Runs headless to avoid opening a browser window
    }

    # Define your search prompt
    prompt = "List me all the traditional recipes from Chioggia and provide a brief description for each."
    
    # Create an instance of SearchGraph with the prompt and configuration.
    search_graph = SearchGraph(
        prompt=prompt,
        config=graph_config
    )

    # Run the search graph to fetch and aggregate the results
    result = search_graph.run()

    # Print the extracted search results
    print("Search Result:")
    print(result)

if __name__ == "__main__":
    main()

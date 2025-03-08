import asyncio
import os
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LlmConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.extraction_strategy import LLMExtractionStrategy

# Define the schema for the extracted data
class CSR_ESG_Link(BaseModel):
    link_url: str = Field(..., description="URL of the CSR or ESG-related document.")
    parent_url: str = Field(..., description="URL of the page containing the link.")
    link_text: str = Field(..., description="Text content of the hyperlink.")

# Asynchronous function to extract CSR and ESG-related links
async def extract_csr_esg_links(urls, max_depth):
    # Configure the browser for headless operation
    browser_config = BrowserConfig(headless=True, verbose=True)
    
    # Configure the LLM with your API key
    llm_config = LlmConfig(provider="openai/gpt-4", api_token=os.getenv('OPENAI_API_KEY'))
    
    # Define the extraction strategy using the LLM
    extraction_strategy = LLMExtractionStrategy(
        llm_config=llm_config,
        schema=CSR_ESG_Link.model_json_schema(),
        extraction_type="schema",
        instruction=(
            "Identify and extract links to documents related to Corporate Social Responsibility (CSR) or "
            "Environment, Social, and Governance (ESG) reports. Provide the link URL, the parent URL, "
            "and the hyperlink's text content. Note that the link URL may not always end with '.pdf'."
        )
    )
    
    # Configure the crawler run settings
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=extraction_strategy,
        max_depth=max_depth
    )

    # Initialize the web crawler
    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = []
        for url in urls:
            # Use Breadth-First Search strategy for deep crawling
            deep_crawl_strategy = BFSDeepCrawlStrategy(crawler, run_config)
            async for result in deep_crawl_strategy.arun(url):
                if result.success and result.extracted_content:
                    # Extract links identified by the LLM as CSR or ESG-related
                    links = [
                        CSR_ESG_Link(
                            link_url=link['link_url'],
                            parent_url=link['parent_url'],
                            link_text=link['link_text']
                        )
                        for link in result.extracted_content.get('links', [])
                    ]
                    results.extend(links)
        return results

# Main function to execute the crawling process
if __name__ == "__main__":
    # List of URLs to crawl
    urls_to_crawl = [
        "https://example.com",
        "https://anotherexample.com"
        # Add more URLs as needed
    ]
    # Set the desired depth
    max_depth = 2
    # Run the asynchronous extraction function
    results = asyncio.run(extract_csr_esg_links(urls_to_crawl, max_depth))
    # Print the extracted links
    for link_info in results:
        print(f"Link URL: {link_info.link_url}")
        print(f"Parent URL: {link_info.parent_url}")
        print(f"Link Text: {link_info.link_text}")
        print("-" * 40)
